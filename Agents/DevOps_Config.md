# Dockerfile

```dockerfile
# Use Node.js LTS Alpine base image
FROM node:18-alpine

# Create app directory
WORKDIR /app

# Install app dependencies
COPY package.json package-lock.json ./

RUN npm ci --only=production

# Copy app source code
COPY . .

# Build app if necessary (for frontend if integrated)
# RUN npm run build

# Expose port where app listens
EXPOSE 3000

# Define environment variable for production
ENV NODE_ENV production

# Start the app
CMD ["node", "src/app.js"]
```

# docker-compose.yml

```yaml
version: '3.8'

services:
  todo-app-backend:
    build: .
    container_name: todo-app-backend
    ports:
      - '3000:3000' # expose container port 3000 to host 3000
    environment:
      - PORT=3000
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/tododb
      - JWT_SECRET=your_jwt_secret_here
    depends_on:
      - db
    restart: always
    volumes:
      - ./:/app

  db:
    image: postgres:15-alpine
    container_name: todo-app-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: tododb
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: always

volumes:
  pgdata:
```

# Deployment Script (optional deploy.sh)

```bash
#!/bin/sh

# Build and start containers in detached mode
docker-compose up -d --build

# Wait for db to be ready
echo "Waiting for database to be ready..."
until docker exec todo-app-db pg_isready -U postgres; do
  sleep 2
done

echo "Database is ready."

# Run migrations or seed scripts if any (optional)
# docker exec todo-app-backend npm run migrate

echo "Deployment completed. Backend running on http://localhost:3000"
```

---

This Dockerfile sets up the Node.js backend environment, installs dependencies, and runs the app on port 3000.

The docker-compose file defines services for the backend app and PostgreSQL database with environment variables configured, volumes for data persistence, network ports mapped, and service dependencies declared.

The optional deployment shell script builds and launches the containers, waits for the database to be ready before signaling deployment completion.

This configuration fully supports easy containerized deployment aligned with the project requirements.