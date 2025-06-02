# UI

## 🧰 Pre-requisites

- Node.js – tested with v22

## 🧱 DevContainer

The preferred way to run the application to use the DevContainer in VSCode, which is preconfigured with the right components and dependencies.

The following instructions assume that they're being executed inside the DevContainer.

## 💻 Install dependencies.

Install dependencies:

```bash
npm install

```

## ⚙️ Running the application

And then run the development server:

```bash
npm run dev
```

Application runs at [http://localhost:3000](http://localhost:3000).

Next.js is actually dog slow, possibly because of the way Docker operates with shared fileystems, so it will take a while to compile and run everything for the first time when compiling the different routes and pages.
