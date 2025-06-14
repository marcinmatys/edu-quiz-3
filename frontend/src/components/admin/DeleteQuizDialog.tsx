import React from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../ui/alert-dialog';

interface DeleteQuizDialogProps {
  isOpen: boolean;
  quizTitle: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DeleteQuizDialog: React.FC<DeleteQuizDialogProps> = ({
  isOpen,
  quizTitle,
  onConfirm,
  onCancel,
}) => {
  return (
    <AlertDialog open={isOpen} onOpenChange={onCancel}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Czy na pewno chcesz usunąć ten quiz?</AlertDialogTitle>
          <AlertDialogDescription>
            Zamierzasz usunąć quiz <strong>"{quizTitle}"</strong>. 
            Ta operacja jest nieodwracalna i spowoduje usunięcie wszystkich powiązanych pytań i odpowiedzi.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Anuluj</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
            Usuń
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}; 