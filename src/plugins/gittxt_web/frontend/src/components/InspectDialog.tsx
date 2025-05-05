import * as Dialog from "@radix-ui/react-dialog";
import { Button } from "@/components/ui/button";

interface Props {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  summary?: {
    total_tokens: number;
    total_files: number;
    language_breakdown: Record<string, number>;
  };
}

export default function InspectDialog({ open, onOpenChange, summary }: Props) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Content className="bg-background p-6 rounded-xl shadow-xl max-w-lg mx-auto">
          <Dialog.Title className="text-lg font-semibold mb-4">Repo Summary</Dialog.Title>
          {summary ? (
            <div className="space-y-3">
              <p>Total files: {summary.total_files}</p>
              <p>Total tokens: {summary.total_tokens}</p>
              <div>
                <h4 className="font-medium mb-1">By language</h4>
                <ul className="list-disc ml-5 space-y-1">
                  {Object.entries(summary.language_breakdown).map(([lang, n]) => (
                    <li key={lang}>{lang}: {n}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Loading …</p>
          )}
          <Dialog.Close asChild>
            <Button className="mt-6 w-full">Close</Button>
          </Dialog.Close>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
