import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('http://localhost:8091/health');
    const data = await response.json();

    return NextResponse.json({
      status: data.status === 'healthy' ? 'healthy' : 'degraded',
      service: {
        status: data.status,
        components: data.components || {},
      },
    });
  } catch (error) {
    console.error('Health check failed:', error);
    return NextResponse.json(
      {
        status: 'unhealthy',
        service: { status: 'unreachable', components: {} },
      },
      { status: 503 }
    );
  }
}