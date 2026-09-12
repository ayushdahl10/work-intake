export interface Items {
  uid: string;
  external_id: string;
  title: string;
  description: string;
  analysisResult: analysisResult;
  analysisError: string;
  status: "RECEIVED" | "ANALYSING" | "READY_FOR_REVIEW" | "COMPLETED" | "FAILED";
  createdAt: string;
  retryCount: number;
}


interface analysisResult {
  summary: string;
  priority: string;
  category: string;
  recommendedAction: string;
}