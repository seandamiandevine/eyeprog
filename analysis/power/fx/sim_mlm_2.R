
library(mnormt)

simulate_lmer = function(formula, dmat, pars, family='binomial', S=1, seed=2023) {
  #' Simulate one lmer response from a formula and design matrix
  #' @param formula: R formula object, in lme4 style
  #' @param DM: Design matrix, with all relevant variables present
  #' @param: S: Number of simulations
  #' @param seed: Random seed.
  #'  
  #' @returns vector with simulated outcome
  
  
  # 1. Extract pars
  gam = pars$GAMMA
  v   = pars$TAU
  sig = pars$SIGMA
  
  # 2. Make mod with simR
  # https://github.com/pitakakariki/simr/blob/0e754a4137ec97a51e883793e16353b4315f83ad/R/new.R
  mod1 = simr::makeGlmer(formula, family=family, gam, v, dmat)
  
  # 3. Return outcome
  y = simulate(mod1, nsim=S, seed = seed, use.u=T)
  
  y
  
}

