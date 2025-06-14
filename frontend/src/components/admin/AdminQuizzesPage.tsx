import React, { useEffect, useState } from 'react';
import { useAdminQuizzes } from '../../lib/hooks/useAdminQuizzes';
import { QuizList } from './QuizList';
import { CreateQuizDialog } from './CreateQuizDialog';
import { QuizEditor } from './QuizEditor';
import { DeleteQuizDialog } from './DeleteQuizDialog';
import type { QuizFilters, QuizListItemVM } from '../../types/quiz';
import { Alert, AlertDescription } from '../ui/alert';
import { Spinner } from '../ui/spinner';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

export const AdminQuizzesPage: React.FC = () => {
  const { quizzes, currentQuiz, isLoading, error, actions } = useAdminQuizzes();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [filters, setFilters] = useState<QuizFilters>({ status: 'all' });
  const [quizToDelete, setQuizToDelete] = useState<QuizListItemVM | null>(null);

  // Pobieranie quizów przy pierwszym renderze
  useEffect(() => {
    actions.fetchQuizzes(filters);
  }, [actions, filters]);

  // Obsługa filtrowania
  const handleFilterChange = (newFilters: QuizFilters) => {
    setFilters(newFilters);
  };

  // Obsługa tworzenia nowego quizu
  const handleCreateQuiz = () => {
    setIsCreateDialogOpen(true);
  };

  // Obsługa zamknięcia dialogu tworzenia quizu
  const handleCloseCreateDialog = () => {
    setIsCreateDialogOpen(false);
  };

  // Obsługa zatwierdzenia formularza tworzenia quizu
  const handleSubmitCreateQuiz = async (data: any) => {
    await actions.createNewQuiz(data);
    setIsCreateDialogOpen(false);
  };

  // Obsługa edycji quizu
  const handleEditQuiz = (quizId: number) => {
    actions.selectQuizForEdit(quizId);
  };

  // Obsługa usunięcia quizu - otwieranie dialogu
  const handleDeleteQuizRequest = (quiz: QuizListItemVM) => {
    setQuizToDelete(quiz);
  };

  // Obsługa potwierdzenia usunięcia quizu
  const handleConfirmDelete = async () => {
    if (quizToDelete) {
      await actions.deleteQuiz(quizToDelete.id);
      setQuizToDelete(null);
    }
  };

  // Obsługa anulowania usunięcia quizu
  const handleCancelDelete = () => {
    setQuizToDelete(null);
  };

  // Obsługa zapisania quizu
  const handleSaveQuiz = async (quizData: any) => {
    await actions.saveQuiz(quizData);
  };

  // Obsługa publikacji quizu
  const handlePublishQuiz = async (quizData: any) => {
    await actions.publishQuiz(quizData);
  };

  // Obsługa anulowania edycji
  const handleCancelEdit = () => {
    actions.clearSelection();
  };

  // Renderowanie komponentu
  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Panel zarządzania quizami</h1>
        <Button onClick={handleCreateQuiz}>
          Stwórz nowy quiz
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error.message}</AlertDescription>
        </Alert>
      )}

      {isLoading && !currentQuiz ? (
        <div className="flex justify-center items-center h-64">
          <Spinner size="lg" />
        </div>
      ) : currentQuiz ? (
        <QuizEditor
          quiz={currentQuiz}
          onSave={handleSaveQuiz}
          onPublish={handlePublishQuiz}
          onCancel={handleCancelEdit}
        />
      ) : (
        <>
          <div className="flex justify-end">
            <Select
              value={filters.status}
              onValueChange={(value) => handleFilterChange({ ...filters, status: value as any })}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Wybierz status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Wszystkie</SelectItem>
                <SelectItem value="draft">Wersje robocze</SelectItem>
                <SelectItem value="published">Opublikowane</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {quizzes.length === 0 ? (
            <div className="text-center py-10">
              <p className="text-lg text-gray-500">Nie znaleziono quizów.</p>
              <p className="text-gray-500">Kliknij "Stwórz nowy quiz", aby rozpocząć.</p>
            </div>
          ) : (
            <QuizList
              quizzes={quizzes}
              onEdit={handleEditQuiz}
              onDelete={handleDeleteQuizRequest}
            />
          )}
        </>
      )}

      <CreateQuizDialog
        isOpen={isCreateDialogOpen}
        onClose={handleCloseCreateDialog}
        onSubmit={handleSubmitCreateQuiz}
      />

      <DeleteQuizDialog
        isOpen={!!quizToDelete}
        quizTitle={quizToDelete?.title || ''}
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
      />
    </div>
  );
}; 