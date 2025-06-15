import { toast } from "sonner";

/**
 * Toast utility functions for displaying notifications
 */

// Success toast with default duration
export const showSuccessToast = (message: string, duration = 3000) => {
  toast.success(message, { duration });
};

// Error toast with longer duration
export const showErrorToast = (message: string, duration = 5000) => {
  toast.error(message, { duration });
};

// Info toast with default duration
export const showInfoToast = (message: string, duration = 3000) => {
  toast.info(message, { duration });
};

// Warning toast with default duration
export const showWarningToast = (message: string, duration = 4000) => {
  toast.warning(message, { duration });
};

// Format error message from API or use default message
export const formatErrorMessage = (error: unknown): string => {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return "Wystąpił nieznany błąd. Spróbuj ponownie później.";
}; 