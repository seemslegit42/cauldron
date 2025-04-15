# Cauldron™ Manifold UI

Manifold is the unified user interface for the Cauldron™ Sentient Enterprise Operating System (sEOS). It provides a modern, responsive, and intuitive interface for interacting with all Cauldron™ modules.

## Architecture

Manifold is built using:

- **React**: A JavaScript library for building user interfaces
- **TypeScript**: For type safety and better developer experience
- **Ant Design**: A design system with a set of high-quality React components
- **Ant Design Pro Components**: Enterprise-class UI components
- **React Router**: For navigation and routing
- **Axios**: For API communication
- **Recharts**: For data visualization
- **TailwindCSS**: For utility-first CSS

## Module Integration

Manifold integrates with the following Cauldron™ modules:

1. **Operations Core**: Core ERP functionality based on Frappe/ERPNext
2. **Synapse™**: Business intelligence and predictive analytics
3. **Aegis Protocol™**: Security monitoring and management
4. **Lore™**: Knowledge management and organizational memory
5. **Command & Cauldron™**: DevOps and infrastructure management

## Development

### Prerequisites

- Node.js 18+
- Yarn or npm

### Setup

1. Clone the repository
2. Install dependencies:
   ```
   yarn install
   ```
   or
   ```
   npm install
   ```

3. Start the development server:
   ```
   yarn start
   ```
   or
   ```
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
REACT_APP_API_URL=http://localhost:80
```

## Building for Production

```
yarn build
```
or
```
npm run build
```

This builds the app for production to the `build` folder.

## License

Apache License 2.0