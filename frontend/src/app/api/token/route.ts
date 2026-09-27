import { NextResponse } from 'next/server';

export const revalidate = 0;

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    const room = url.searchParams.get('room') || url.searchParams.get('room_name') || 'jarvis-room';
    const identity = url.searchParams.get('name') || url.searchParams.get('identity') || `user_${Math.floor(1000 + Math.random() * 9000)}`;

    const backendUrl = process.env.JARVIS_BACKEND_URL || 'http://127.0.0.1:8000';
    const targetUrl = `${backendUrl}/api/livekit/token?room=${encodeURIComponent(room)}&identity=${encodeURIComponent(identity)}`;

    const res = await fetch(targetUrl, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
    });

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error?.message || 'Failed to fetch token from Jarvis backend' },
      { status: 500 }
    );
  }
}

export async function POST(req: Request) {
  return GET(req);
}
