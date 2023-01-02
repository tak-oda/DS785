# Workforce Planning Tool for the consulting industry using LinkedIn data
# Abstract
I developed a Workforce Planning Tool to help a management consulting executive to launch a new service line and plan the organization structure aligned with its growth goal. As rapid change in talent demands in the management consulting industry, the tool aimed to give a simulation of career progressions for emerging professionals whose pattern is not well known in traditional consultants and recommend recruiting plan to maximize future revenue growth. Literature review confirmed applications of stochastic processes to organizations dynamism, e.g., recruiting, promotion and resignation. Additional review found operations research methods to solve human resource assignment problems. In this study, I used LinkedIn user profile from a bench mark firm to imitate a new organization. 502 LinkedIn profiles from Deloitte Digital UK was trained on a Semi-Markov model to forecast future organization structure. Semi-Markov Chain was implemented via msSurv R package to model the transition probabilities between job titles. Finally, a Linear Programming was solved to generate optimized number of additional recruits to maximize revenue growth in five years. It obtained approximately 535% revenue growth with additional 269 recruits for five years planning horizon. The sensitivity analysis revealed that retention of Associate level is critical to make the organization structure grow healthy. The tool also demonstrated the capability to control preferable ratio between staff and managers through solving optimized recruiting plan. With the capability the different recruiting plans were obtained for the typical organization strategies (1) Junior leveraging and (2) Gray Hair model. While demonstrated the usefulness of LinkedIn data as an organization benchmark on Workforce Planning, lessons such as lower sample size, time consuming data collection were left for a future opportunity. 
  <br> Keywords: Workforce Planning, Professional Services, Markov Chain, LinkedIn