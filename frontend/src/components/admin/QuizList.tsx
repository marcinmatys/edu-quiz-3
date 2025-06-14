import React from 'react';
import type { QuizListItemVM } from '../../types/quiz';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { CalendarIcon, Edit as EditIcon, Trash2 as TrashIcon } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { pl } from 'date-fns/locale';

interface QuizListProps {
  quizzes: QuizListItemVM[];
  onEdit: (quizId: number) => void;
  onDelete: (quiz: QuizListItemVM) => void;
}

export const QuizList: React.FC<QuizListProps> = ({ quizzes, onEdit, onDelete }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {quizzes.map((quiz) => (
        <Card key={quiz.id} className="overflow-hidden">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start">
              <CardTitle className="text-xl">{quiz.title}</CardTitle>
              <Badge variant={quiz.status === 'published' ? 'default' : 'outline'}>
                {quiz.status === 'published' ? 'Opublikowany' : 'Wersja robocza'}
              </Badge>
            </div>
          </CardHeader>
          
          <CardContent className="pb-2">
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Poziom:</span>
                <span>{quiz.level}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Liczba pytań:</span>
                <span>{quiz.question_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Ostatnia aktualizacja:</span>
                <div className="flex items-center">
                  <CalendarIcon className="h-3.5 w-3.5 mr-1 text-muted-foreground" />
                  <span>
                    {formatDistanceToNow(new Date(quiz.updated_at), {
                      addSuffix: true,
                      locale: pl
                    })}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
          
          <CardFooter className="pt-2 flex justify-end gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => onEdit(quiz.id)}
            >
              <EditIcon className="h-4 w-4 mr-1" />
              Edytuj
            </Button>
            <Button 
              variant="destructive" 
              size="sm" 
              onClick={() => onDelete(quiz)}
            >
              <TrashIcon className="h-4 w-4 mr-1" />
              Usuń
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}; 