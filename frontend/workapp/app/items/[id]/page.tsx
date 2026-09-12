import Link from "next/link";
import type { Items } from "@/types/item";
import { ItemDetailsClient } from "@/components/item-details-client";

async function getItem(id: string): Promise<Items> {
  const res = await fetch(`http://localhost:8000/api/work-item/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch work item detail");
  }

  return res.json();
}

export default async function ItemPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const item = await getItem(id);

  return (
    <div className="container">
      <div className="detail-wrap">
        <Link href="/" className="back-link">
          ← Back to list
        </Link>

        <ItemDetailsClient item={item} />
      </div>
    </div>
  );
}
