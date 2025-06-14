import React, { useEffect, useState } from 'react';
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import type { CreateQuizRequestDto, LevelDto } from '../../types/quiz';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { Button } from '../ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../ui/form';
import { Input } from '../ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import { api } from '../../lib/api';

interface CreateQuizDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateQuizRequestDto) => void;
}

const formSchema = z.object({
  topic: z.string().min(1, 'Temat jest wymagany'),
  title: z.string().min(3, 'Tytuł musi mieć co najmniej 3 znaki'),
  question_count: z.coerce
    .number()
    .int()
    .min(5, 'Minimalna liczba pytań to 5')
    .max(20, 'Maksymalna liczba pytań to 20'),
  level_id: z.coerce.number().int().positive('Wybierz poziom'),
});

export const CreateQuizDialog: React.FC<CreateQuizDialogProps> = ({
  isOpen,
  onClose,
  onSubmit,
}) => {
  const [levels, setLevels] = useState<LevelDto[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      topic: '',
      title: '',
      question_count: 10,
      level_id: undefined,
    },
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

    if (isOpen) {
      fetchLevels();
      form.reset();
    }
  }, [isOpen, form]);

  const handleSubmit = (values: z.infer<typeof formSchema>) => {
    onSubmit(values as CreateQuizRequestDto);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Stwórz nowy quiz</DialogTitle>
          <DialogDescription>
            Wypełnij formularz, aby wygenerować nowy quiz przy pomocy AI.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tytuł quizu</FormLabel>
                  <FormControl>
                    <Input placeholder="Wprowadź tytuł quizu" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="topic"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Temat</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Np. Fotosynteza, Wojny napoleońskie, Równania kwadratowe"
                      {...field}
                    />
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
                    onValueChange={(value) => field.onChange(parseInt(value))}
                    value={field.value?.toString()}
                    disabled={isLoading}
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

            <FormField
              control={form.control}
              name="question_count"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Liczba pytań</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      min={5}
                      max={20}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
              >
                Anuluj
              </Button>
              <Button
                type="submit"
                disabled={isLoading || !form.formState.isValid}
              >
                Generuj
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}; 