"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Image, Video, Send, Loader2, Download } from "lucide-react"

type GenerationType = "image" | "video"
type GenerationStatus = "idle" | "generating" | "success" | "error"

interface GenerationResult {
  url: string
  prompt: string
  type: GenerationType
}

export default function Home() {
  const [prompt, setPrompt] = useState("")
  const [generationType, setGenerationType] = useState<GenerationType>("image")
  const [status, setStatus] = useState<GenerationStatus>("idle")
  const [errorMessage, setErrorMessage] = useState("")
  const [results, setResults] = useState<GenerationResult[]>([])

  const handleGenerate = async () => {
    if (!prompt.trim()) return

    setStatus("generating")
    setErrorMessage("")

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          type: generationType,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || "Generation failed")
      }

      if (data.data && data.data[0]?.url) {
        const newResult: GenerationResult = {
          url: data.data[0].url,
          prompt: prompt.trim(),
          type: generationType,
        }
        setResults((prev) => [newResult, ...prev])
        setPrompt("")
        setStatus("success")
      } else {
        throw new Error("No image/video URL in response")
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to generate")
      setStatus("error")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleGenerate()
    }
  }

  const handleDownload = async (url: string, filename: string) => {
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = blobUrl
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(blobUrl)
    } catch (error) {
      console.error("Download failed:", error)
    }
  }

  return (
    <div className="flex h-screen w-full flex-col bg-background">
      {/* Header */}
      <header className="flex items-center justify-center border-b border-border/40 bg-card px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="text-xl font-bold tracking-tight text-foreground">Multimodal AI</span>
          <span className="rounded-full bg-teal-600 px-2 py-0.5 text-[10px] font-semibold text-white">
            {generationType === "image" ? "Image" : "Video"}
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-4xl px-4 py-6">
          {/* Results Gallery */}
          {results.length > 0 && (
            <div className="mb-6 space-y-4">
              <h2 className="text-sm font-semibold text-muted-foreground">Recent Generations</h2>
              <div className="grid gap-4 sm:grid-cols-2">
                {results.map((result, index) => (
                  <Card key={index} className="group relative overflow-hidden border-border/50 bg-card shadow-sm">
                    <div className="aspect-square w-full overflow-hidden">
                      {result.type === "image" ? (
                        <img
                          src={result.url}
                          alt={result.prompt}
                          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                          loading="lazy"
                        />
                      ) : (
                        <video
                          src={result.url}
                          className="h-full w-full object-cover"
                          controls
                          muted
                          loop
                          playsInline
                        />
                      )}
                    </div>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                      <div className="absolute bottom-0 left-0 right-0 p-3">
                        <p className="text-xs text-white line-clamp-2 mb-2">{result.prompt}</p>
                        <div className="flex items-center gap-2">
                          <span className="rounded bg-white/20 px-2 py-0.5 text-[10px] text-white backdrop-blur-sm">
                            {result.type === "image" ? "Image" : "Video"}
                          </span>
                          <Button
                            size="sm"
                            variant="secondary"
                            className="h-6 px-2 text-[10px]"
                            onClick={() =>
                              handleDownload(
                                result.url,
                                `${result.type}-${Date.now()}.${result.type === "image" ? "png" : "mp4"}`
                              )
                            }
                          >
                            <Download className="h-3 w-3 mr-1" />
                            Download
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Status Messages */}
          {status === "generating" && (
            <Card className="mb-6 border-teal-500/30 bg-teal-500/10 p-4">
              <div className="flex items-center gap-3">
                <Loader2 className="h-5 w-5 animate-spin text-teal-600" />
                <div>
                  <p className="text-sm font-medium text-foreground">Generating {generationType}...</p>
                  <p className="text-xs text-muted-foreground">This may take 30-60 seconds</p>
                </div>
              </div>
            </Card>
          )}

          {status === "error" && (
            <Card className="mb-6 border-red-500/30 bg-red-500/10 p-4">
              <p className="text-sm text-red-600">{errorMessage}</p>
              <Button
                size="sm"
                variant="outline"
                className="mt-2 h-7 text-xs"
                onClick={() => setStatus("idle")}
              >
                Dismiss
              </Button>
            </Card>
          )}
        </div>
      </main>

      {/* Input Area */}
      <footer className="border-t border-border/40 bg-card px-4 py-4">
        <div className="mx-auto max-w-4xl space-y-3">
          {/* Type Selector */}
          <div className="flex items-center justify-center gap-2">
            <Button
              variant={generationType === "image" ? "default" : "outline"}
              size="sm"
              onClick={() => setGenerationType("image")}
              className={generationType === "image" ? "bg-teal-600 hover:bg-teal-700" : ""}
            >
              <Image className="h-4 w-4 mr-2" />
              Image
            </Button>
            <Button
              variant={generationType === "video" ? "default" : "outline"}
              size="sm"
              onClick={() => setGenerationType("video")}
              className={generationType === "video" ? "bg-teal-600 hover:bg-teal-700" : ""}
            >
              <Video className="h-4 w-4 mr-2" />
              Video
            </Button>
          </div>

          {/* Prompt Input */}
          <div className="relative">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                generationType === "image"
                  ? "Describe the image you want to create... (e.g., 'A futuristic cityscape at sunset with flying cars')"
                  : "Describe the video you want to create... (e.g., 'A robot walking through a forest with sunlight filtering through trees')"
              }
              className="min-h-[80px] w-full resize-none rounded-xl border-2 border-teal-500/20 bg-background px-4 py-3 pr-12 text-sm text-foreground placeholder:text-muted-foreground/60 focus:border-teal-500/50 focus:outline-none focus:ring-1 focus:ring-teal-500/20"
            />
            <Button
              size="icon"
              onClick={handleGenerate}
              disabled={!prompt.trim() || status === "generating"}
              className="absolute right-2 bottom-2 h-8 w-8 rounded-lg bg-teal-600 text-white transition-all hover:bg-teal-700 disabled:opacity-50"
            >
              {status === "generating" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Quick Prompts */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
            <span className="text-xs text-muted-foreground">Try:</span>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs"
              onClick={() =>
                setPrompt("A futuristic cityscape at sunset with flying cars and neon lights, cyberpunk style")
              }
            >
              🌆 Futuristic City
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs"
              onClick={() =>
                setPrompt("A friendly robot walking through a lush forest with sunlight filtering through trees")
              }
            >
              🤖 Robot in Nature
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="h-7 text-xs"
              onClick={() =>
                setPrompt("An astronaut exploring a distant planet with two moons and alien vegetation, space exploration")
              }
            >
              🚀 Space Exploration
            </Button>
          </div>
        </div>
      </footer>
    </div>
  )
}
