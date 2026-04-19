# where2sit Architecture

## Overview

where2sit is a Django-based web application designed to improve the visibility and flexibility of campus spaces. The system supports room booking, availability checking, user ratings, comments, and favorites, serving students, faculty, and administrators.

The provided diagram outlines a typical web architecture for a Django application, illustrating how data and requests flow between the user and various backend services. Here is a breakdown of the components and their interactions:

Web-Client and Nginx: The user (web-client) initiates the process. For static assets like CSS, JavaScript, or images, the client interacts directly with Nginx. This offloads the burden of serving simple files from the main application server, improving efficiency.

Django Web Server: For dynamic content, the client sends an HTTP request to the Django Web Server. This acts as the "brain" of the operation, processing logic and coordinating between other systems. It is also connected to Nginx to manage how static files are collected or served.

Database and Third-Party Services: To fulfill a request, the Django server communicates with a Database to retrieve or store persistent data (like user profiles or posts). Simultaneously, it can reach out to Third-party services via external APIs—such as payment gateways or social media integrations—to extend the application's functionality beyond its own codebase.

## Diagram

![System Architecture](docs/system-architecture.png)

