
library(mnormt)

sim1 = function(formula, DM, pars, family='binomial', seed=2023) {
  #' Simulate one lmer response from a formula and design matrix
  #' @param formula: R formula object, in lme4 style
  #' @param DM: Design matrix, with all relevant variables present
  #' @param seed: Random seed.
  #'  
  #' @returns vector with simulated outcome
  
  
  set.seed(seed)  
  
  # 1. Extract pars
  gam = pars$GAMMA
  v   = pars$TAU
  sig = pars$SIGMA
  

  # 2. Extract vars from formula
  preds = attributes(terms(formula))$term.labels
  f     = preds[!grepl('\\|',preds)]
  r     = gsub(' ', '', strsplit(preds[grepl('\\|',preds)],'\\|')[[1]])
  g     = r[length(r)]
  r     = r[-length(r)][1]
  r     = strsplit(r,'\\+')[[1]]
  
  dmat = cbind(DM[,g], 1, DM[,f])
  n    = length(unique(dmat[,1]))
  
  # 3. Sample random effects (level-2)
  Uj = rmnorm(n, mean = rep(0, length(r)+1), varcov = v) # intercept, slopes
  
  # 4. Sample residuals (level-1)
  if(family=='gaussian') Rij = rnorm(nrow(dmat), 0, sqrt(sig))
  
  # 5. Compute betas as GAMMA + Uj
  # First, add zero column for fixed effects only
  gam_m = matrix(gam, n,length(gam), byrow = TRUE)
  
  if(ncol(Uj)!=ncol(gam_m)) {
    diff = ncol(gam_m) - ncol(Uj)
    if(diff < 0) stop('VarCov mispecified')
    for(i in 1:diff) Uj = cbind(Uj, 0)
  }
  b = gam_m + Uj
  
  # 6. Compute response
  y = rowSums(dmat[,-1]*b[dmat[,1],])
  
  # 7. Compute as response
  if(family =='binomial') {
    p   = plogis(y)
    y01 = sapply(p, function(i) sample(c(0,1),prob = c(1-i,i),size = 1)) # rbinom(1,1,i))
  }
  
  y01
  
  
  # test
  # DM$y = y01
  # mod = glmer(y ~ prog_c + trial0_c + trial02_c + prog_c:trial0_c + prog_c:trial02_c +
  #               (1|id), data=DM, family='binomial', nAGQ = 0)
  # x = summary(mod)
  # x$coefficients[,'Estimate']
  # pars$GAMMA
  # 
  # p = tapply(predict(mod, type='response'), list(DM$trial0_c, DM$prog_c), mean)
  # matplot(p, type='l', lty=1, lwd=2)
  
  
}

simulate_lmer = function(formula, DM, pars, nsim, family='binomial', seed=2022) {
  #' Wrapper for sim1(), which reproduces the process `nsim` times
  
  set.seed(seed)
  sapply(1:nsim, function(i) sim1(formula, DM, pars, family, runif(1,0,1e6)))
  
}
