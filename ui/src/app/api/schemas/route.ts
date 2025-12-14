import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const domain = searchParams.get('domain') || undefined;

    const url = domain ?
      `http://localhost:8091/schemas?domain=${domain}` :
      'http://localhost:8091/schemas';

    const response = await fetch(url);
    const data = await response.json();

    return NextResponse.json({
      schemas: data.schemas || [],
    });
  } catch (error) {
    console.error('Get schemas failed:', error);
    return NextResponse.json(
      { error: 'Failed to fetch schemas' },
      { status: 500 }
    );
  }
}