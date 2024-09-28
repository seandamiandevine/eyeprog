
rm(list=ls())

library(lme4)
library(beepr) # for ding
source('fx/sim_mlm.R')
ci = function(x, a=qnorm(.975), na.rm=T) plotrix::std.error(x, na.rm=na.rm)*a

set.seed(2023)

# Constants ---------------------------------------------------------------

# Sample info
N = seq(20,100,by=20)
J = 50
S = 100 # number of sims.
a = .05

# Predictors
prog    = c(0,1)
trial   = 1:J
n_rep   = 16

prog_c   = prog-.5
trial0   = trial/max(trial)
trial0_c = trial0 - median(trial0)

trial02 = trial0^2
trial02_c = trial02 - median(trial02)

# fixed effects (log odds)

lor2p = function(x) exp(sum(x))/(1+exp(sum(x)))

GAMMA = c('(Intercept)' = -3.5, 
          'prog_c'    = 1,
          'trial0_c'  = 0, 
          'trial02_c' = 0, 
          'prog_c:trial0_c' = .1, 
          'prog_c:trial02_c'=  2) 


# random variance 
TAU   = c('id.(Intercept)' = .25, 
          'id.prog_c'    = 0.1,
          'id.trial0_c'  = .001, 
          'id.trial02_c' = .001, 
          'id.prog_c:trial0_c' = 0.001, 
          'id.prog_c2:trial0_c'=  0.001) 

TAU_mat = matrix(0, length(TAU), length(TAU)) # no par corr
diag(TAU_mat) = TAU

PARS = list(GAMMA=GAMMA, TAU=TAU_mat)


# Prediction plot ---------------------------------------------------------
pdf('figs/predictions.pdf', 6, 6)

n = 100

X = data.frame(prog_c = rep(prog_c, each=n))
X[,'trial0_c']   = rep(approx(trial0_c, n=n)$y, length(prog_c)) 
X[,'trial02_c']  = rep(approx(trial02_c, n=n)$y, length(prog_c)) 
X[,'prog_c:trial0_c']  = X$prog_c*X$trial0_c
X[,'prog_c:trial02_c'] = X$prog_c*X$trial02_c

y = GAMMA[1] + GAMMA[2]*X$prog_c + GAMMA[3]*X$trial0_c+ GAMMA[4]*X$trial02_c + 
  GAMMA[5]*X$`prog_c:trial0_c` + GAMMA[6]*X$`prog_c:trial02_c`

m = tapply(y, list(X$trial0_c, X$prog_c), mean)
p = plogis(m)
cols = c('grey','darkgreen')#colorRampPalette(c('red','blue'))(nrow(p))

matplot(p, type='l', lty=1,lwd=3, col=cols, ylim=c(0,.2), xaxt='n', 
        xlab='Trial', ylab='P(Look)', main='')

axis(1, at = seq(1, nrow(p), l=6), labels=floor(seq(1, max(trial), l=6)))
legend('topleft',bty='n', col=cols,lty=1,lwd=3, legend=c('No Progress','Progress'))

dev.off()

# Simulate ----------------------------------------------------------------

DM = expand.grid(prog_c = rep(prog_c, each=J), block = 1:(n_rep/length(prog)))
DM[,'trial0_c']   = rep(trial0_c, n_rep)
DM[,'trial02_c']  = rep(trial02_c, n_rep)
DM[,'prog_c:trial0_c']  = DM$prog_c*DM$trial0_c
DM[,'prog_c:trial02_c'] = DM$prog_c*DM$trial02_c


out = matrix(NA, length(N)*S, 15, 
             dimnames = list(NULL, c('n','s', 
                                     'b0_b','prog_b', 'trial_b', 'trial2_b','prog_trial_b','prog_trial2_b', 
                                     'b0_p','prog_p', 'trial_p', 'trial2_p','prog_trial_p','prog_trial2_p', 
                                     'conv')))
row = 1   


for(i in seq(N)) {
  
  cat('\n~~~~~~~~~~~~~~~~~ Testing Sample Size', i, '/', length(N), '~~~~~~~~~~~~~~~~~ \n')
  
  dmat = do.call(rbind, replicate(N[i], DM, simplify=FALSE))
  dmat$id = rep(1:N[i], each=J*n_rep)
  
  formula = y ~ prog_c + trial0_c + trial02_c + prog_c:trial0_c + prog_c:trial02_c + (prog_c + trial0_c + trial02_c + prog_c:trial0_c + prog_c:trial02_c|id)
  y = simulate_lmer(formula, dmat, PARS, S, family='binomial')

  # p = tapply(y[,1], list(dmat$trial0_c, dmat$prog_c), mean)
  # matplot(p, type='l', lty=1, lwd=2)

  pb = txtProgressBar(1, S)
  for(s in 1:S) {
    
    setTxtProgressBar(pb, s)
    
    dmat$y = y[,s]
    # don't do random effects for first pass 
    mod  = glmer(y ~ prog_c + trial0_c + trial02_c + prog_c:trial0_c + prog_c:trial02_c + (1|id),
                 data=dmat, family='binomial', nAGQ = 0)
    sum  = summary(mod)
    
    out[row,] = c(N[i], s, sum$coefficients[,'Estimate'], sum$coefficients[,'Pr(>|z|)'], mod@optinfo$conv$opt)
    row = row+1
    
  }
  
  cat('\n P(Sig | N=',N[i],',',' a=',a, ') = ', mean(out[out[,'n']==N[i],'prog_trial2_p'] < a, na.rm=T), '\n', sep = '')
  
}

out = as.data.frame(out)
write.csv(out, paste0('power_sim_s',S,'.csv'))

beep()

# Visualize ---------------------------------------------------------------


## last simulation ----

pdf('figs/last_sim.pdf', 6, 6)

cols = c('grey','darkgreen')

p = tapply(dmat$y, list(dmat$trial0_c, dmat$prog_c), mean)
matplot(p, type='l', lty=1, lwd=3, col=cols, ylim=c(0, .2), 
        xlab='Trial', ylab='Simulated P(Look)')
legend('topleft',bty='n', col=cols,lty=1,lwd=3, legend=c('No Progress','Progress'))

dev.off()

## curve -----


out = read.csv(paste0('power_sim_s',S,'.csv'))

# double check estimated vs. true GAMMAs
colMeans(out[,grepl('_b', colnames(out))])

target_pwr = .8

out$sig = as.numeric(out$prog_trial2_p < a)

psig = tapply(out$sig, out$n, mean)
csig = tapply(out$sig, out$n, ci)

pdf('figs/power_curve.pdf', 6, 6)

plot(psig, ylim=c(0,1), xlab='Sample Size', ylab='P(Significant)', type='b', pch=16, 
     main = '', xaxt='n')
axis(1, at=1:length(psig), labels=names(psig))
arrows(seq(psig), psig-csig, seq(psig), psig+csig, length=0)
abline(h=target_pwr, lty=2 )

dev.off()


# interpolate -------------------------------------------------------------

psig_approx = approx(x=names(psig), y=psig, n = 100)

## Closest to 90% power
psig_approx$x[which.min(abs(psig_approx$y-.9))]
