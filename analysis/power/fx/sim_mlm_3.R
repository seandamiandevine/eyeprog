
library(mnormt)

sim1 = function(formula, DM, pars, family='binomial', seed=2023) {
  #' Simulate one lmer response from a formula and design matrix
  #' @param formula: R formula object, in lme4 style
  #' @param DM: Design matrix, with all relevant variables present
  #' @param seed: Random seed.
  #'  
  #' @returns vector with simulated outcome
  
  
  set.seed(seed)  
  
  
  # 1. Extract vars from formula
  preds = attributes(terms(formula))$term.labels
  f     = preds[!grepl('\\|',preds)]
  r     = gsub(' ', '', strsplit(preds[grepl('\\|',preds)],'\\|')[[1]])
  g     = r[length(r)]
  r     = r[-length(r)][1]
  r     = strsplit(r,'\\+')[[1]]
  
  dmat = cbind(DM[,g], 1, DM[,f])
  n    = length(unique(dmat[,1]))
  
  # 2. XB
  X  = as.matrix(dmat[,-1])
  B  = as.matrix(pars$GAMMA)
  XB = X %*% B
  
  
  # 3. Zb
  # Design matrix for random effects is a bit tricky to put together
  # We want a block-diagonal matrix; each block has a little design matrix for each participant
  Z = Matrix::bdiag(lapply(unique(dmat[,1]), function(x) cbind(1,as.matrix(dmat[dmat[,1]==x,r]))))
  V = pars$TAU
  u = rmnorm(n, mean = rep(0, length(r)+1), varcov = V)
  b = as.matrix(c(t(u)))
  Zb = Z%*%b
  
  # residuals
  # TODO
  
  # 4. Compute response
  y = as.vector(XB + Zb)
  
  if(family =='binomial') {
    p   = plogis(y)
    y01 = sapply(p, function(i) sample(c(0,1),prob = c(1-i,i),size = 1)) # rbinom(1,1,i))
  }
  
  y01
  
  
  # test.
  DM$y = y01
  mod = glmer(formula, data=DM, family='binomial', nAGQ = 0)
  x = summary(mod)
  x$coefficients[,'Estimate']
  pars$GAMMA
  
}

simulate_lmer = function(formula, DM, pars, nsim, family='binomial', seed=2022) {
  #' Wrapper for sim1(), which reproduces the process `nsim` times
  
  set.seed(seed)
  sapply(1:nsim, function(i) sim1(formula, DM, pars, family, runif(1,0,1e6)))
  
}
