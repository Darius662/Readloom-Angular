export interface Collection {
  id: number;
  name: string;
  description?: string;
  type: string;
  is_default?: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface CollectionItem {
  id: number;
  collection_id: number;
  series_id: number;
  status?: 'owned' | 'reading' | 'completed' | 'wishlist';
  notes?: string;
  rating?: number;
  progress?: number;
  added_at?: string;
}

export interface CollectionStats {
  total_items: number;
  total_series: number;
  total_chapters: number;
  total_volumes: number;
}
