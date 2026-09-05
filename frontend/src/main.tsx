import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import App from "./App";
import { AuthBoundary } from "./auth/AuthBoundary";
import "./styles.css";
import "./explorer.css";
import "./operations.css";
import "./operationalValue.css";
import "./auth.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1_000,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

const root = document.getElementById("root");
if (!root) throw new Error("root element missing");

const product = <App />;
const browserAuthEnabled = import.meta.env.VITE_BROWSER_AUTH_ENABLED === "true";

createRoot(root).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      {browserAuthEnabled ? <AuthBoundary>{product}</AuthBoundary> : product}
    </QueryClientProvider>
  </StrictMode>,
);
