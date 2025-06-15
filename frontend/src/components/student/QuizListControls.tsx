import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import type { SortParams } from "../../types/quiz";

interface QuizListControlsProps {
  sortParams: SortParams;
  onSortChange: (newParams: SortParams) => void;
}

/**
 * Component that provides controls for sorting the quiz list
 */
export function QuizListControls({ sortParams, onSortChange }: QuizListControlsProps) {
  // Handle sort option change
  const handleSortChange = (value: string) => {
    // Parse the combined value (field:order)
    const [sortBy, order] = value.split(":");
    onSortChange({ sortBy, order: order as 'asc' | 'desc' });
  };

  // Create the combined sort value
  const sortValue = `${sortParams.sortBy}:${sortParams.order}`;

  return (
    <div className="flex justify-end mb-4">
      <div className="flex items-center gap-2">
        <span className="text-sm text-muted-foreground">Sortuj według:</span>
        <Select value={sortValue} onValueChange={handleSortChange}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Wybierz opcję" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="level:asc">Poziom (rosnąco)</SelectItem>
            <SelectItem value="level:desc">Poziom (malejąco)</SelectItem>
            <SelectItem value="title:asc">Tytuł (A-Z)</SelectItem>
            <SelectItem value="title:desc">Tytuł (Z-A)</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
} 