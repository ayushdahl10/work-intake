from node:20.9.0

WORKDIR /app

COPY package.json .
COPY pnpm-lock.yaml .

RUN npm install -g pnpm@10.5.2
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 3000
CMD ["pnpm", "run", "dev"]

