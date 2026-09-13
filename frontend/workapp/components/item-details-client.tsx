"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import type { Items } from "@/types/item";
import { useRouter } from "next/navigation";
import { apiUrl } from "@/lib/api";

type ItemDetailsClientProps = {
  item: Items;
};

export function ItemDetailsClient({ item }: ItemDetailsClientProps) {
  const [currentItem, setCurrentItem] = useState<Items>(item);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  async function handleAction(action: "complete" | "re-analyze") {
    setLoading(true);

    const endpoint =
      action === "complete"
        ? apiUrl(`/api/work-item/${currentItem.uid}/complete`)
        : apiUrl(`/api/work-item/${currentItem.uid}/trigger`);

    const res = await fetch(endpoint, {
      method: action === "complete" ? "PATCH" : "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!res.ok) {
      throw new Error(
        action === "complete"
          ? "Failed to complete work item"
          : "Failed to re-analyze work item"
      );
    }

    const updatedItem = await res.json();
    setCurrentItem(updatedItem);
    setLoading(false);
    router.push('/');
  }

  return (
    <div className="detail-card">
      <p className="detail-label">External ID</p>
      <h1>{currentItem.external_id}</h1>

      <div className="detail-grid">
        <div>
          <p className="detail-label">Title</p>
          <p>{currentItem.title}</p>
        </div>

        <div>
          <p className="detail-label">Status</p>
          <p>{currentItem.status}</p>
        </div>

        <div>
          <p className="detail-label">Retry Count</p>
          <p>{currentItem.retryCount}</p>
        </div>
      </div>

      <div>
        <p className="detail-label">Description</p>
        <p>{currentItem.description}</p>
      </div>

      {currentItem.analysisResult && (
        <div>
          <p className="detail-label pt-2">Analysis Result</p>
          <div className="p-4 border rounded-sm shadow-sm space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-lg">
                {currentItem.analysisResult.summary}
              </span>
              <span className="px-2 py-1 text-xs font-bold text-red-700 bg-red-100 rounded">
                {currentItem.analysisResult.priority}
              </span>
            </div>
            <p className="text-sm text-gray-600">
              Category: {currentItem.analysisResult.category}
            </p>
            <p className="text-sm text-gray-800">
              Action: {currentItem.analysisResult.recommendedAction}
            </p>
          </div>
        </div>
      )}

      {currentItem.analysisError && (
        <div>
          <p className="detail-label pt-2">Analysis Error</p>
          <div className="p-4 border rounded-sm shadow-sm space-y-2">
            <p className="text-sm text-gray-800">{currentItem.analysisError}</p>
          </div>
        </div>
      )}

      <div className="py-2">
        {currentItem.status === "FAILED" || currentItem.status === "RECEIVED" && ( 
          <Button
            type="button"
            onClick={() => void handleAction("re-analyze")}
            disabled={loading}
            className="bg-red-500 hover:bg-red-600 text-white"
          >
            {loading ? "Re-analyzing..." : "ReAnalyze"}
          </Button>
        )}

        {currentItem.status === "READY_FOR_REVIEW" && (
          <Button
            type="button"
            onClick={() => void handleAction("complete")}
            disabled={loading}
            className="bg-lime-600 hover:bg-lime-700 text-white"
          >
            {loading ? "Completing..." : "Complete"}
          </Button>
        )}
      </div>
    </div>
  );
}
