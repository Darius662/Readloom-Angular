export interface Author {
  id: number;
  name: string;
  bio?: string;
  photo_url?: string;
  birth_date?: string;
  nationality?: string;
  website?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AuthorMetadata {
  author_id: number;
  goodreads_id?: string;
  wikipedia_url?: string;
  external_links?: { [key: string]: string };
  subjects?: string[];
  notable_works?: string[];
}
