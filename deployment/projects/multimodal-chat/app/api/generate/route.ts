import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { prompt, type } = await request.json()

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      )
    }

    const apiKey = process.env.DASHSCOPE_API_KEY
    const baseUrl = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'

    // Determine model based on type
    const model = type === 'video' ? 'wan2.1-t2v' : 'qwen-image-2.0-pro'

    const response = await fetch(`${baseUrl}/images/generations`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: model,
        prompt: prompt,
        n: 1,
        size: '1024x1024',
      }),
    })

    const data = await response.json()

    if (!response.ok) {
      console.error('DashScope API error:', data)
      return NextResponse.json(
        { 
          error: data.error?.message || 'Generation failed',
          code: data.error?.code || response.status
        },
        { status: response.status }
      )
    }

    return NextResponse.json({
      success: true,
      data: data.data,
      model: model,
    })
  } catch (error) {
    console.error('Internal error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
