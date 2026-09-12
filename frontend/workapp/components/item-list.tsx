"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Items } from "@/types/item";
import { apiUrl } from "@/lib/api";

type StatusFilter = "ALL" | Items["status"];

type TableListProps = {
  items: Items[];
};

const statusOptions: StatusFilter[] = [
  "ALL",
  "RECEIVED",
  "ANALYSING",
  "READY_FOR_REVIEW",
  "COMPLETED",
  "FAILED",
];

export function TableList() {
  const router = useRouter();
  const [selectedStatus, setSelectedStatus] = useState<StatusFilter>("ALL");
  const [items, setItems] = useState<Items[]>([]);
  const [filteredItems, setFilteredItems] = useState<Items[]>([]);

  useEffect(() => {
    let isActive = true;

    async function fetchAllItems() {
      const res = await fetch(apiUrl("/api/work-item"), {
        cache: "no-store",
      });

      if (!res.ok) {
        throw new Error("Failed to fetch work items");
      }

      const data: Items[] = await res.json();

      if (isActive) {
        setItems(data);
        setFilteredItems(data);
      }
    }

    void fetchAllItems();

    return () => {
      isActive = false;
    };
  }, []);

  useEffect(() => {
    if (selectedStatus === "ALL") {
      setFilteredItems(items);
      return;
    }

    let isActive = true;

    async function fetchFilteredItems() {
      const url = apiUrl(
        `/api/work-item?status=${encodeURIComponent(selectedStatus)}`
      );

      const res = await fetch(url, {
        cache: "no-store",
      });

      if (!res.ok) {
        throw new Error("Failed to fetch filtered work items");
      }

      const data: Items[] = await res.json();

      if (isActive) {
        setFilteredItems(data);
      }
    }

    void fetchFilteredItems();

    return () => {
      isActive = false;
    };
  }, [items, selectedStatus]);

  return (
    <div>
      <div className="mb-4 flex items-center justify-end">
        <label htmlFor="status-filter" className="mr-2 text-sm font-medium">
          Status
        </label>
        <select
          id="status-filter"
          value={selectedStatus}
          onChange={(event) => {
            setSelectedStatus(event.target.value as StatusFilter);
          }}
          className="rounded border border-gray-300 bg-white px-3 py-2 text-sm"
        >
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {status === "ALL" ? "All" : status}
            </option>
          ))}
        </select>
      </div>

      <Table>
        <TableCaption>A list of work items</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>External ID</TableHead>
            <TableHead>Title</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Retry Count</TableHead>
            <TableHead>Action</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredItems.map((item) => (
            <TableRow
              key={item.uid}
              className="cursor-pointer"
              onClick={() => router.push(`/items/${item.uid}`)}
            >
              <TableCell className="font-medium">{item.external_id}</TableCell>
              <TableCell>{item.title}</TableCell>
              <TableCell>{item.status}</TableCell>
              <TableCell>{item.retryCount}</TableCell>
              <TableCell>
                <button
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    router.push(`/items/${item.uid}`);
                  }}
                  className="text-blue-600 underline hover:text-blue-800"
                >
                  Open
                </button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
