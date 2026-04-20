# where2Sit Architecture

## Component Diagram

![High-Level Diagram](images/ComponentDiagram.png)

As shown in the diagram, the user interacts through the browser, prompting a request through our frontend which passes it on to our Django backend. The backend handles logic and requests which communicates with our database that stores room and reservation data. For development, we are continuing to use Django's default SQLite with plans to convert to PostgreSQL in production should we reach that step in order to better work with our Render deployment.
