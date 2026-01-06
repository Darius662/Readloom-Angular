import { Injectable } from '@angular/core';
import { Series, Chapter, Volume, Release } from '../models/series.model';
import { Collection, CollectionItem } from '../models/collection.model';
import { Author } from '../models/author.model';
import { CalendarEvent } from '../models/calendar.model';

@Injectable({
  providedIn: 'root'
})
export class MockDataService {
  constructor() {}

  getMockSeries(): Series[] {
    return [
      {
        id: 1,
        name: 'One Piece',
        type: 'manga',
        description: 'A pirate adventure series',
        cover_url: 'https://placehold.co/200x300?text=One+Piece',
        status: 'ongoing',
        total_chapters: 1050,
        total_volumes: 105,
        rating: 4.8,
        created_at: '2023-01-01',
        updated_at: '2025-12-19'
      },
      {
        id: 2,
        name: 'Naruto',
        type: 'manga',
        description: 'A ninja adventure series',
        cover_url: 'https://placehold.co/200x300?text=Naruto',
        status: 'completed',
        total_chapters: 700,
        total_volumes: 72,
        rating: 4.7,
        created_at: '2023-01-02',
        updated_at: '2025-12-19'
      },
      {
        id: 3,
        name: 'Attack on Titan',
        type: 'manga',
        description: 'A dark fantasy series',
        cover_url: 'https://placehold.co/200x300?text=Attack+on+Titan',
        status: 'completed',
        total_chapters: 139,
        total_volumes: 34,
        rating: 4.6,
        created_at: '2023-01-03',
        updated_at: '2025-12-19'
      },
      {
        id: 4,
        name: 'Death Note',
        type: 'manga',
        description: 'A psychological thriller',
        cover_url: 'https://placehold.co/200x300?text=Death+Note',
        status: 'completed',
        total_chapters: 108,
        total_volumes: 12,
        rating: 4.5,
        created_at: '2023-01-04',
        updated_at: '2025-12-19'
      },
      {
        id: 5,
        name: 'My Hero Academia',
        type: 'manga',
        description: 'A superhero series',
        cover_url: 'https://placehold.co/200x300?text=My+Hero+Academia',
        status: 'ongoing',
        total_chapters: 425,
        total_volumes: 43,
        rating: 4.4,
        created_at: '2023-01-05',
        updated_at: '2025-12-19'
      },
      {
        id: 6,
        name: 'Demon Slayer',
        type: 'manga',
        description: 'A demon hunting series',
        cover_url: 'https://placehold.co/200x300?text=Demon+Slayer',
        status: 'completed',
        total_chapters: 205,
        total_volumes: 23,
        rating: 4.6,
        created_at: '2023-01-06',
        updated_at: '2025-12-19'
      }
    ];
  }

  getMockCollections(): Collection[] {
    return [
      {
        id: 1,
        name: 'Favorites',
        description: 'My favorite manga and comics',
        type: 'manga',
        is_default: true,
        created_at: '2023-01-01',
        updated_at: '2025-12-19'
      },
      {
        id: 2,
        name: 'Reading',
        description: 'Currently reading',
        type: 'manga',
        is_default: false,
        created_at: '2023-01-02',
        updated_at: '2025-12-19'
      },
      {
        id: 3,
        name: 'Completed',
        description: 'Finished reading',
        type: 'manga',
        is_default: false,
        created_at: '2023-01-03',
        updated_at: '2025-12-19'
      }
    ];
  }

  getMockAuthors(): Author[] {
    return [
      {
        id: 1,
        name: 'Eiichiro Oda',
        bio: 'Creator of One Piece',
        photo_url: 'https://placehold.co/200x200?text=Eiichiro+Oda',
        birth_date: '1975-01-01',
        nationality: 'Japanese',
        created_at: '2023-01-01',
        updated_at: '2025-12-19'
      },
      {
        id: 2,
        name: 'Masashi Kishimoto',
        bio: 'Creator of Naruto',
        photo_url: 'https://placehold.co/200x200?text=Masashi+Kishimoto',
        birth_date: '1974-11-08',
        nationality: 'Japanese',
        created_at: '2023-01-02',
        updated_at: '2025-12-19'
      },
      {
        id: 3,
        name: 'Hajime Isayama',
        bio: 'Creator of Attack on Titan',
        photo_url: 'https://placehold.co/200x200?text=Hajime+Isayama',
        birth_date: '1986-08-29',
        nationality: 'Japanese',
        created_at: '2023-01-03',
        updated_at: '2025-12-19'
      },
      {
        id: 4,
        name: 'Tsugumi Ohba',
        bio: 'Creator of Death Note',
        photo_url: 'https://placehold.co/200x200?text=Tsugumi+Ohba',
        birth_date: '1981-01-01',
        nationality: 'Japanese',
        created_at: '2023-01-04',
        updated_at: '2025-12-19'
      }
    ];
  }

  getMockCalendarEvents(): CalendarEvent[] {
    const today = new Date();
    return [
      {
        id: 1,
        seriesId: 1,
        seriesTitle: 'One Piece',
        contentType: 'MANGA',
        type: 'chapter',
        number: 1051,
        title: 'Chapter 1051',
        releaseDate: new Date(today.getTime() + 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        is_confirmed: true,
        cover_url: 'https://placehold.co/200x300?text=One+Piece'
      },
      {
        id: 2,
        seriesId: 5,
        seriesTitle: 'My Hero Academia',
        contentType: 'MANGA',
        type: 'chapter',
        number: 426,
        title: 'Chapter 426',
        releaseDate: new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        is_confirmed: true,
        cover_url: 'https://placehold.co/200x300?text=My+Hero+Academia'
      },
      {
        id: 3,
        seriesId: 6,
        seriesTitle: 'Attack on Titan',
        contentType: 'MANGA',
        type: 'volume',
        number: 34,
        title: 'Volume 34',
        releaseDate: new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        is_confirmed: true,
        cover_url: 'https://placehold.co/200x300?text=Attack+on+Titan'
      },
      {
        id: 4,
        seriesId: 1,
        seriesTitle: 'One Piece',
        contentType: 'MANGA',
        type: 'volume',
        number: 105,
        title: 'Volume 105',
        releaseDate: new Date(today.getTime() + 5 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        is_confirmed: false,
        cover_url: 'https://placehold.co/200x300?text=One+Piece+Vol+105'
      }
    ];
  }
}
