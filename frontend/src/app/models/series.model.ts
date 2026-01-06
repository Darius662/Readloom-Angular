export interface Series {
  id: number;
  name: string;
  type: 'manga' | 'manwa' | 'comic' | 'book';
  title?: string;
  author?: string;
  publisher?: string;
  isbn?: string;
  published_date?: string;
  subjects?: string | string[];
  description?: string;
  cover_url?: string;
  status?: 'ongoing' | 'completed' | 'hiatus';
  total_chapters?: number;
  total_volumes?: number;
  rating?: number;
  star_rating?: number;
  reading_progress?: number;
  user_description?: string;
  content_type?: string;
  created_at?: string;
  updated_at?: string;
  // Want to Read specific properties
  in_library?: number;
  want_to_read?: number;
  collection_names?: string;
  volume_count?: number;
  total_value?: number;
  owned_volumes?: number;
  metadata_id?: string;
  metadata_source?: string;
  provider?: string; // Added for search compatibility
  alternative_titles?: string[];
  genres?: string[];
}

export interface Chapter {
  id: number;
  series_id: number;
  chapter_number: number;
  title?: string;
  release_date?: string;
  status?: string;
  read_status?: string;
  is_confirmed?: boolean;
}

export interface Volume {
  id: number;
  series_id: number;
  volume_number: number;
  title?: string;
  description?: string;
  cover_url?: string;
  cover_path?: string;
  release_date?: string;
  is_confirmed?: boolean;
  created_at?: string;
  updated_at?: string;
  chapters?: Chapter[]; // Optional: chapters in this volume
}

export interface Release {
  id: number;
  series_id: number;
  type: 'chapter' | 'volume';
  number: number;
  title?: string;
  release_date: string;
  is_confirmed: boolean;
}
