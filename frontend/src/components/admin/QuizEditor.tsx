import React, { useState, useEffect } from 'react';
import { z } from 'zod';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { v4 as uuidv4 } from 'uuid';
import type { QuizEditorVM, LevelDto } from '../../types/quiz';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue 
} from '../ui/select';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../ui/form';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Spinner } from '../ui/spinner';
import { PlusCircle, Trash2, Save, Check, X } from 'lucide-react';
import { api } from '../../lib/api';

interface QuizEditorProps {
  quiz: QuizEditorVM;
  onSave: (quizData: QuizEditorVM) => void;
  onPublish: (quizData: QuizEditorVM) => void;
  onCancel: () => void;
}

const formSchema = z.object({
  title: z.string().min(3, 'Tytuł musi mieć co najmniej 3 znaki'),
  level_id: z.coerce.number().int().positive('Wybierz poziom'),
  questions: z.array(
    z.object({
      id: z.number().optional(),
      uiId: z.string(),
      text: z.string().min(5, 'Pytanie musi mieć co najmniej 5 znaków'),
      answers: z.array(
        z.object({
          id: z.number().optional(),
          uiId: z.string(),
          text: z.string().min(1, 'Odpowiedź nie może być pusta'),
          is_correct: z.boolean(),
        })
      ).min(2, 'Pytanie musi mieć co najmniej 2 odpowiedzi')
      .refine(
        (answers) => answers.filter(a => a.is_correct).length === 1,
        'Pytanie musi mieć dokładnie jedną poprawną odpowiedź'
      ),
    })
  ).min(1, 'Quiz musi mieć co najmniej jedno pytanie'),
});

type FormValues = z.infer<typeof formSchema>;

export const QuizEditor: React.FC<QuizEditorProps> = ({ quiz, onSave, onPublish, onCancel }) => {
  const [levels, setLevels] = useState<LevelDto[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Inicjalizacja formularza
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: quiz.title,
      level_id: quiz.level_id,
      questions: quiz.questions,
    },
  });

  // Obsługa tablicy pytań
  const { fields: questionFields, append: appendQuestion, remove: removeQuestion } = useFieldArray({
    control: form.control,
    name: 'questions',
  });

  // Pobieranie poziomów (klas)
  useEffect(() => {
    const fetchLevels = async () => {
      try {
        setIsLoading(true);
        const data = await api.get<LevelDto[]>('/levels/');
        setLevels(data);
      } catch (error) {
        console.error('Błąd pobierania poziomów:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLevels();
  }, []);

  // Dodawanie nowego pytania
  const handleAddQuestion = () => {
    appendQuestion({
      uiId: uuidv4(),
      text: '',
      answers: [
        { uiId: uuidv4(), text: '', is_correct: true },
        { uiId: uuidv4(), text: '', is_correct: false },
      ],
    });
  };

  // Zapisywanie quizu
  const handleSave = (data: FormValues) => {
    onSave(data as QuizEditorVM);
  };

  // Publikowanie quizu
  const handlePublish = () => {
    const data = form.getValues();
    onPublish(data as QuizEditorVM);
  };

  // Renderowanie komponentu
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Edycja quizu</h2>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onCancel}>
            <X className="mr-2 h-4 w-4" />
            Anuluj
          </Button>
          <Button variant="default" onClick={form.handleSubmit(handleSave)}>
            <Save className="mr-2 h-4 w-4" />
            Zapisz
          </Button>
          <Button variant="default" onClick={form.handleSubmit(handlePublish)}>
            <Check className="mr-2 h-4 w-4" />
            Publikuj
          </Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center h-64">
          <Spinner size="lg" />
        </div>
      ) : (
        <Form {...form}>
          <form className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tytuł quizu</FormLabel>
                    <FormControl>
                      <Input {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="level_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Poziom</FormLabel>
                    <Select
                      onValueChange={(value: string) => field.onChange(parseInt(value))}
                      value={field.value?.toString()}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Wybierz poziom" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {levels.map((level) => (
                          <SelectItem key={level.id} value={level.id.toString()}>
                            {level.code} - {level.description}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Pytania</h3>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddQuestion}
                >
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Dodaj pytanie
                </Button>
              </div>

              {questionFields.length === 0 ? (
                <div className="text-center py-10 border rounded-md">
                  <p className="text-gray-500">Brak pytań. Kliknij "Dodaj pytanie", aby rozpocząć.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {questionFields.map((field, questionIndex) => (
                    <QuestionEditor
                      key={field.id}
                      form={form}
                      questionIndex={questionIndex}
                      onRemove={() => removeQuestion(questionIndex)}
                    />
                  ))}
                </div>
              )}
            </div>
          </form>
        </Form>
      )}
    </div>
  );
};

interface QuestionEditorProps {
  form: any;
  questionIndex: number;
  onRemove: () => void;
}

const QuestionEditor: React.FC<QuestionEditorProps> = ({ form, questionIndex, onRemove }) => {
  const { fields: answerFields, append: appendAnswer, remove: removeAnswer } = useFieldArray({
    control: form.control,
    name: `questions.${questionIndex}.answers`,
  });

  // Dodawanie nowej odpowiedzi
  const handleAddAnswer = () => {
    appendAnswer({
      uiId: uuidv4(),
      text: '',
      is_correct: false,
    });
  };

  // Ustawianie poprawnej odpowiedzi
  const handleSetCorrectAnswer = (answerIndex: number) => {
    // Ustawiamy wszystkie odpowiedzi jako niepoprawne
    answerFields.forEach((_, index) => {
      form.setValue(`questions.${questionIndex}.answers.${index}.is_correct`, false);
    });
    
    // Ustawiamy wybraną odpowiedź jako poprawną
    form.setValue(`questions.${questionIndex}.answers.${answerIndex}.is_correct`, true);
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">
          Pytanie {questionIndex + 1}
        </CardTitle>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={onRemove}
          className="h-8 w-8 p-0"
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent className="space-y-4">
        <FormField
          control={form.control}
          name={`questions.${questionIndex}.text`}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Treść pytania</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">Odpowiedzi</h4>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={handleAddAnswer}
            >
              <PlusCircle className="mr-2 h-3 w-3" />
              Dodaj odpowiedź
            </Button>
          </div>

          <div className="space-y-2">
            {answerFields.map((field, answerIndex) => (
              <div key={field.id} className="flex items-center gap-2">
                <div className="flex-1">
                  <FormField
                    control={form.control}
                    name={`questions.${questionIndex}.answers.${answerIndex}.text`}
                    render={({ field }) => (
                      <FormItem>
                        <FormControl>
                          <Input {...field} placeholder={`Odpowiedź ${answerIndex + 1}`} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <Button
                  type="button"
                  variant={form.watch(`questions.${questionIndex}.answers.${answerIndex}.is_correct`) ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleSetCorrectAnswer(answerIndex)}
                  className="min-w-24"
                >
                  {form.watch(`questions.${questionIndex}.answers.${answerIndex}.is_correct`) ? "Poprawna" : "Ustaw jako poprawną"}
                </Button>
                {answerFields.length > 2 && (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeAnswer(answerIndex)}
                    className="h-8 w-8 p-0"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 