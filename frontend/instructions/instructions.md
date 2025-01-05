# Product Requirements Document (PRD)

## Introduction
This Product Requirements Document (PRD) outlines the specifications for developing a single-page React application designed to assist mental health counselors and other users in leveraging backend Retrieval-Augmented Generation (RAG) capabilities. The application will facilitate users in submitting free-text questions and receiving generated answers from the backend.

## Project Overview
We aim to build a user-friendly, scalable, and maintainable single-page application (SPA) using React. The application will allow mental health counselors and other users to interact with a backend service that utilizes RAG to generate meaningful responses based on user queries.

### Key Features
- User Input: Users can submit free-text questions related to mental health.
- Loading Indicator: A visual indicator will display while awaiting a response from the backend.
- Answer Display: Generated answers from the backend will be displayed to the user.
- State Management: Previous questions and answers will be cleared when a new question is submitted.

## Objectives
- User Experience: Provide a seamless and intuitive interface for users to interact with the backend RAG service.
- Performance: Ensure quick loading times and responsive interactions.
- Scalability: Design the application structure to accommodate future features and growth.
- Maintainability: Establish a clear and organized file structure to facilitate easy updates and collaboration.

## Scope

### In-Scope
- Development of the front-end using React, TypeScript, Tailwind CSS, and Lucid Icons.
- Integration with the backend API for generating answers based on user questions.
- Implementation of core functionalities including input handling, loading indicators, and answer display.
- Creation of a well-structured file system to support the application's scalability and maintainability.

### Out-of-Scope
- Backend development and maintenance.
- User authentication and authorization.
- Deployment and DevOps configurations.

## Functional Requirements

### Question Input
**Description**: Allow users to input free-text questions.

**Details**:
- Provide a textarea for question input.
- Include a submit button to send the question to the backend.
- Validate input to ensure non-empty submissions.

### Loading Indicator
**Description**: Display a loading spinner or indicator while awaiting the backend response.

**Details**:
- The indicator should be visible immediately after the question is submitted.
- It should disappear once the response is received.

### Answer Display
**Description**: Show the generated answer from the backend.

**Details**:
- Present the answer in a readable format.
- Ensure the answer area is cleared when a new question is submitted.

### State Management
**Description**: Manage the state of questions and answers.

**Details**:
- Clear previous questions and answers upon submitting a new question.
- Handle loading states and potential errors gracefully.

### Responsive Design
**Description**: Ensure the application is responsive across various devices.

**Details**:
- Utilize Tailwind CSS for styling to achieve responsiveness.
- Test the application on different screen sizes.

## Non-Functional Requirements

### Performance
- Optimize rendering to ensure smooth user interactions.
- Minimize the number of API calls to prevent unnecessary load.

### Usability
- Design an intuitive and accessible user interface.
- Provide clear feedback to users during interactions.

### Maintainability
- Organize codebase with a clear and modular file structure.
- Use TypeScript for type safety and easier debugging.

### Scalability
- Design the architecture to support future feature additions without major overhauls.

### Security
- Ensure secure handling of user inputs to prevent potential vulnerabilities.

## Technical Stack

### Front-End
- Framework: React
- Language: TypeScript
- Styling: Tailwind CSS
- Icons: Lucid Icons

### Backend Integration
- API Communication: Axios or Fetch API

### Version Control
- Repository: Git (hosted on platforms like GitHub, GitLab, etc.)

## File Structure
A well-organized file structure is essential for the scalability and maintainability of the application. Below is the recommended file structure with explanations for each directory and file.

```
my-app/
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       └── images/
├── src/
│   ├── assets/
│   │   ├── icons/
│   │   │   └── [Lucid Icons]
│   │   └── styles/
│   │       └── tailwind.css
│   ├── components/
│   │   ├── AnswerDisplay/
│   │   │   ├── AnswerDisplay.tsx
│   │   │   └── AnswerDisplay.module.css
│   │   ├── LoadingIndicator/
│   │   │   ├── LoadingIndicator.tsx
│   │   │   └── LoadingIndicator.module.css
│   │   ├── QuestionInput/
│   │   │   ├── QuestionInput.tsx
│   │   │   └── QuestionInput.module.css
│   │   └── common/
│   │       ├── Button.tsx
│   │       └── [Other Reusable Components].tsx
│   ├── hooks/
│   │   └── useConversation.ts
│   ├── services/
│   │   └── api.ts
│   ├── types/
│   │   └── index.d.ts
│   ├── utils/
│   │   └── [Utility Functions].ts
│   ├── App.tsx
│   ├── index.tsx
│   └── react-app-env.d.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── package.json
├── .gitignore
└── README.md
```

### Detailed Breakdown

#### 1. Root Directory (my-app/)
- `package.json`: Manages project dependencies, scripts, and metadata.
- `tsconfig.json`: Configures TypeScript settings.
- `tailwind.config.js` & `postcss.config.js`: Configure Tailwind CSS and PostCSS respectively.
- `.gitignore`: Specifies intentionally untracked files to ignore (e.g., node_modules/).
- `README.md`: Provides an overview and documentation for the project.

#### 2. Public Directory (public/)
- `index.html`: The main HTML file that serves the React app.
- `favicon.ico`: The icon displayed in the browser tab.
- `assets/images/`: Store static images used in the app.

#### 3. Source Directory (src/)

##### a. Assets (src/assets/)
- `icons/`: Contains Lucid Icons or other SVGs used throughout the app.
- `styles/tailwind.css`: Entry point for Tailwind CSS styles.

##### b. Components (src/components/)
Organize components by feature or functionality. Each component has its own folder containing the component file and associated styles.

###### AnswerDisplay/
- `AnswerDisplay.tsx`: Displays the generated answer from the backend.
- `AnswerDisplay.module.css`: Scoped CSS for the component (optional if using Tailwind exclusively).

###### LoadingIndicator/
- `LoadingIndicator.tsx`: Shows a loading spinner or indicator while awaiting backend response.
- `LoadingIndicator.module.css`: Scoped CSS for the component.

###### QuestionInput/
- `QuestionInput.tsx`: Input field for users to submit their free-text questions.
- `QuestionInput.module.css`: Scoped CSS for the component.

###### common/
- `Button.tsx`: A reusable button component.
- `[Other Reusable Components].tsx`: Any other components that are used across multiple parts of the app.

##### c. Hooks (src/hooks/)
- `useConversation.ts`: Custom React hook to manage the conversation state, including sending questions to the backend and handling responses.

##### d. Services (src/services/)
- `api.ts`: Contains functions to interact with the backend API.

```typescript
// src/services/api.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const generateAnswer = async (question: string) => {
  const response = await axios.post(`${API_BASE_URL}/conversations/generate`, {
    question,
  }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data.answer;
};
```

##### e. Types (src/types/)
- `index.d.ts`: Define TypeScript interfaces and types used across the application.

```typescript
// src/types/index.d.ts
export interface ApiResponse {
  answer: string;
}

export interface Conversation {
  question: string;
  answer: string;
}
```

##### f. Utilities (src/utils/)
- `[Utility Functions].ts`: Any helper functions that assist with data manipulation, formatting, etc.

##### g. Main Application Files
- `App.tsx`: The root React component that orchestrates other components.
- `index.tsx`: Entry point that renders the App component into the DOM.
- `react-app-env.d.ts`: Provides TypeScript definitions for the React app environment.

## API Documentation

### Backend Endpoint
The frontend will interact with the backend's RAG capabilities through a RESTful API. Below are the details for the required endpoint.

#### Generate Answer

**Endpoint**:
```bash
POST http://localhost:8000/api/v1/conversations/generate
```

**Headers**:
```bash
Content-Type: application/json
```

**Request Body**:
```json
{
  "question": "I have been feeling anxious about my job interview"
}
```

**cURL Example**:
```bash
curl -X POST http://localhost:8000/api/v1/conversations/generate \
  -H "Content-Type: application/json" \
  -d '{"question": "I have been feeling anxious about my job interview"}'
```

**Successful Response**:
Status Code: 200 OK

Body:
```json
{
  "answer": "It's normal to feel anxious before a job interview. Remember to focus on your strengths and practice good communication skills."
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "error": "Invalid question format."
}
```

500 Internal Server Error:
```json
{
  "error": "An unexpected error occurred. Please try again later."
}
```

## Additional Considerations

### 1. State Management
For the current scope, React's built-in state management using useState and useReducer hooks will be sufficient. However, if the application scales in the future, consider integrating a state management library such as Redux or Zustand.

### 2. Routing
Given that this is a single-page application with a primary focus on one main view, React Router may not be necessary at this stage. However, if future features introduce multiple views or pages, setting up React Router early can be beneficial.

### 3. Testing
Implement a testing strategy to ensure code reliability and quality.

**Testing Libraries**:
- Jest: For unit and integration testing.
- React Testing Library: For testing React components.

**Test Directory**:
- Create a `__tests__/` directory inside `src/` to house test files.

### 4. Linting and Formatting
Maintain code quality and consistency across the codebase.

**Tools**:
- ESLint: For identifying and fixing linting issues.
- Prettier: For code formatting.

**Configuration Files**:
- `.eslintrc.js`
- `.prettierrc`

### 5. Environment Variables
Use environment variables to manage configuration settings, such as the backend API URL.

**.env File**:
```bash
REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
```

**Usage in Code**:
```typescript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
```

### 6. Error Handling
Implement robust error handling to manage API errors and display meaningful messages to users.

**Global Error Handling**:
- Create an ErrorBoundary component to catch and display errors in the UI.

**API Error Handling**:
- Handle HTTP errors gracefully and provide user-friendly feedback.

### 7. Accessibility
Ensure the application is accessible to all users by adhering to accessibility standards.

**Best Practices**:
- Use semantic HTML elements.
- Provide ARIA labels where necessary.
- Ensure sufficient color contrast.
- Enable keyboard navigation.

### 8. Performance Optimization
Optimize the application for better performance.

**Techniques**:
- Code splitting and lazy loading of components.
- Minimize bundle size.
- Optimize images and assets.
