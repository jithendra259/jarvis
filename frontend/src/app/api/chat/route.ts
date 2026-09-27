import { NextResponse } from 'next/server';

export const revalidate = 0;

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const backendUrl = process.env.JARVIS_BACKEND_URL || 'http://127.0.0.1:8000';
    const targetUrl = `${backendUrl}/api/chat`;

    const res = await fetch(targetUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error: any) {
    return NextResponse.json(
      { error: error?.message || 'Backend connection error' },
      { status: 500 }
    );
  }
}
