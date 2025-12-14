import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import type { GenerateRequestBody } from '@/types/api';

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const body: GenerateRequestBody = await request.json();

    // Build gRPC request payload
    const grpcRequest = {
      request_id: `ui-${Date.now()}`,
      domain: body.domain,
      entity: body.entity,
      count: body.count || 10,
      context: body.context,
      scenarios: body.scenarios,
      hints: body.hints,
      inline_schema: body.inlineSchema,
      // Note: generation_path is not a field in the protobuf schema
      // Routing is done based on hints and context
    };

    // Remove undefined fields
    const cleanRequest = JSON.parse(JSON.stringify(grpcRequest));

    // Call grpcurl
    const command = `echo '${JSON.stringify(cleanRequest)}' | grpcurl -plaintext -d @ localhost:9091 testdata.v1.TestDataService/GenerateData`;

    try {
      const { stdout, stderr } = await execAsync(command);

      if (stderr && !stderr.includes('WARNING')) {
        console.error('grpcurl error:', stderr);
        throw new Error(stderr);
      }

      const grpcResponse = JSON.parse(stdout);

      // Parse the data field from JSON string
      let parsedData;
      try {
        parsedData = JSON.parse(grpcResponse.data || '[]');
      } catch {
        parsedData = grpcResponse.data || [];
      }

      return NextResponse.json({
        success: grpcResponse.success,
        requestId: grpcResponse.request_id,
        data: parsedData,
        recordCount: grpcResponse.record_count,
        metadata: {
          generationPath: grpcResponse.metadata?.generation_path,
          llmTokensUsed: grpcResponse.metadata?.llm_tokens_used,
          generationTimeMs: grpcResponse.metadata?.generation_time_ms,
          coherenceScore: grpcResponse.metadata?.coherence_score,
          scenarioCounts: grpcResponse.metadata?.scenario_counts || {},
        },
        error: grpcResponse.error,
      });
    } catch (execError: any) {
      console.error('Failed to execute grpcurl:', execError);
      throw new Error(`Failed to connect to backend service: ${execError.message}`);
    }
  } catch (error) {
    console.error('Generate data failed:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'Generation failed',
      },
      { status: 500 }
    );
  }
}