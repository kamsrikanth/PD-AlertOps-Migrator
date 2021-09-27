# PD-AlertOps-Migrator
Migrator script for porting users/groups/schedules from PagerDuty to AlertOps

==============================================================================

*****Code is currently in draft mode (working), need to organize it more (split up into multiple files for functionality division and clarity); and migration currently works for users and groups*****



- To run the application UI, make sure you have Python v3.5 or above. 
- To open the application,  run the command in terminal/your editor as - 'python pd_ao_mg.py"
- To install any Python packages you might not have - execute the following commands (THIS IS ONLY IF THE PROGRAM DOESNT RUN AS EXPECTED, IT SHOULD WORK FINE)

'*pip install pipreqs*'

'*pipreqs .*'

This will generate a 'requirements.txt' file and you can install packages with the consequent command '*pip install -r requirements.txt*'

- You will need the PagerDuty API Key (v2, with full access) and the AlertOps v2 API Key [REMEMBER this works only with the v2 version of AlertOps' API)

- On providing the API Keys, you should be able to retrieve the Teams from PagerDuty, you can select multiple teams, or a single team, and the corresponding users in each team will be migrated to AlertOps.

- If no team is available or selected, you will just be migrating the Users from PagerDuty to AlertOps
