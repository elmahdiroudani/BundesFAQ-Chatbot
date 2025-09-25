const BACKEND_URI = "";

import { ChatAppResponse, ChatAppResponseOrError, ChatAppRequest, Config, SimpleAPIResponse, HistoryListApiResponse, HistoryApiResponse } from "./models";
import { useLogin, getToken, isUsingAppServicesLogin } from "../authConfig";

export async function getHeaders(idToken: string | undefined): Promise<Record<string, string>> {
    // If using login and not using app services, add the id token of the logged in account as the authorization
    if (useLogin && !isUsingAppServicesLogin) {
        if (idToken) {
            return { Authorization: `Bearer ${idToken}` };
        }
    }

    return {};
}

export async function configApi(): Promise<Config> {
    try {
        const response = await fetch(`${BACKEND_URI}/config`, {
            method: "GET"
        });
        return (await response.json()) as Config;
    } catch (error) {
        console.warn("Backend not available, using mock config");
        // Mock configuration for development without backend
        return {
            defaultReasoningEffort: "medium",
            showMultimodalOptions: false,
            showSemanticRankerOption: true,
            showQueryRewritingOption: true,
            showReasoningEffortOption: false,
            streamingEnabled: true,
            showVectorOption: true,
            showUserUpload: true,
            showLanguagePicker: true,
            showSpeechInput: false,
            showSpeechOutputBrowser: false,
            showSpeechOutputAzure: false,
            showChatHistoryBrowser: true,
            showChatHistoryCosmos: false,
            showAgenticRetrievalOption: false,
            ragSearchTextEmbeddings: true,
            ragSearchImageEmbeddings: false,
            ragSendTextSources: true,
            ragSendImageSources: false
        } as Config;
    }
}

export async function askApi(request: ChatAppRequest, idToken: string | undefined): Promise<ChatAppResponse> {
    try {
        const headers = await getHeaders(idToken);
        const response = await fetch(`${BACKEND_URI}/ask`, {
            method: "POST",
            headers: { ...headers, "Content-Type": "application/json" },
            body: JSON.stringify(request)
        });

        if (response.status > 299 || !response.ok) {
            throw Error(`Request failed with status ${response.status}`);
        }
        const parsedResponse: ChatAppResponseOrError = await response.json();
        if (parsedResponse.error) {
            throw Error(parsedResponse.error);
        }

        return parsedResponse as ChatAppResponse;
    } catch (error) {
        console.warn("Backend not available, using mock response");
        // Mock response for development without backend
        const lastMessage = request.messages[request.messages.length - 1];
        return {
            message: {
                content: `This is a mock response to your question: "${lastMessage.content}"\n\nThe BundesFAQ Chatbot backend is not currently running. To get real responses about German federal laws and regulations, you'll need to:\n\n1. Set up and start your backend server\n2. Configure the API endpoints properly\n3. Connect to Azure OpenAI or another LLM service\n\nFor now, this frontend is working in demo mode.`,
                role: "assistant"
            },
            delta: {
                content: "",
                role: "assistant"
            },
            context: {
                data_points: {
                    text: [],
                    images: [],
                    citations: []
                },
                followup_questions: [
                    "How do I set up the backend?",
                    "What APIs need to be implemented?",
                    "How do I connect to Azure OpenAI?"
                ],
                thoughts: [
                    {
                        title: "Mock Response",
                        description: "Backend server not available - displaying demo response"
                    }
                ]
            },
            session_state: null
        } as ChatAppResponse;
    }
}

export async function chatApi(request: ChatAppRequest, shouldStream: boolean, idToken: string | undefined): Promise<Response> {
    let url = `${BACKEND_URI}/chat`;
    if (shouldStream) {
        url += "/stream";
    }
    try {
        const headers = await getHeaders(idToken);
        return await fetch(url, {
            method: "POST",
            headers: { ...headers, "Content-Type": "application/json" },
            body: JSON.stringify(request)
        });
    } catch (error) {
        console.warn("Backend not available, creating mock streaming response");
        // Create a mock response for development
        const lastMessage = request.messages[request.messages.length - 1];
        const mockResponse = `This is a mock streaming response to: "${lastMessage.content}"\n\nThe BundesFAQ Chatbot backend is not currently running. This frontend is working in demo mode.\n\nTo get real responses about German federal laws and regulations, you'll need to set up your backend server.`;
        
        // Create a readable stream that mimics the backend response
        const stream = new ReadableStream({
            start(controller) {
                const chunks = mockResponse.split(' ');
                let i = 0;
                
                const sendChunk = () => {
                    if (i < chunks.length) {
                        const chunk = {
                            message: {
                                content: chunks[i] + ' ',
                                role: "assistant"
                            },
                            delta: {
                                content: chunks[i] + ' ',
                                role: "assistant"
                            },
                            context: {
                                data_points: {
                                    text: [],
                                    images: [],
                                    citations: []
                                },
                                followup_questions: null,
                                thoughts: []
                            },
                            session_state: null
                        };
                        
                        controller.enqueue(new TextEncoder().encode(JSON.stringify(chunk) + '\n'));
                        i++;
                        setTimeout(sendChunk, 100); // Simulate streaming delay
                    } else {
                        controller.close();
                    }
                };
                
                sendChunk();
            }
        });
        
        return new Response(stream, {
            headers: { 'Content-Type': 'application/x-ndjson' }
        });
    }
}

export async function getSpeechApi(text: string): Promise<string | null> {
    return await fetch("/speech", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            text: text
        })
    })
        .then(response => {
            if (response.status == 200) {
                return response.blob();
            } else if (response.status == 400) {
                console.log("Speech synthesis is not enabled.");
                return null;
            } else {
                console.error("Unable to get speech synthesis.");
                return null;
            }
        })
        .then(blob => (blob ? URL.createObjectURL(blob) : null));
}

export function getCitationFilePath(citation: string): string {
    // If there are parentheses at end of citation, remove part in parentheses
    const cleanedCitation = citation.replace(/\s*\(.*?\)\s*$/, "").trim();
    return `${BACKEND_URI}/content/${cleanedCitation}`;
}

export async function uploadFileApi(request: FormData, idToken: string): Promise<SimpleAPIResponse> {
    const response = await fetch("/upload", {
        method: "POST",
        headers: await getHeaders(idToken),
        body: request
    });

    if (!response.ok) {
        throw new Error(`Uploading files failed: ${response.statusText}`);
    }

    const dataResponse: SimpleAPIResponse = await response.json();
    return dataResponse;
}

export async function deleteUploadedFileApi(filename: string, idToken: string): Promise<SimpleAPIResponse> {
    const headers = await getHeaders(idToken);
    const response = await fetch("/delete_uploaded", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ filename })
    });

    if (!response.ok) {
        throw new Error(`Deleting file failed: ${response.statusText}`);
    }

    const dataResponse: SimpleAPIResponse = await response.json();
    return dataResponse;
}

export async function listUploadedFilesApi(idToken: string): Promise<string[]> {
    const response = await fetch(`/list_uploaded`, {
        method: "GET",
        headers: await getHeaders(idToken)
    });

    if (!response.ok) {
        throw new Error(`Listing files failed: ${response.statusText}`);
    }

    const dataResponse: string[] = await response.json();
    return dataResponse;
}

export async function postChatHistoryApi(item: any, idToken: string): Promise<any> {
    const headers = await getHeaders(idToken);
    const response = await fetch("/chat_history", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(item)
    });

    if (!response.ok) {
        throw new Error(`Posting chat history failed: ${response.statusText}`);
    }

    const dataResponse: any = await response.json();
    return dataResponse;
}

export async function getChatHistoryListApi(count: number, continuationToken: string | undefined, idToken: string): Promise<HistoryListApiResponse> {
    const headers = await getHeaders(idToken);
    let url = `${BACKEND_URI}/chat_history/sessions?count=${count}`;
    if (continuationToken) {
        url += `&continuationToken=${continuationToken}`;
    }

    const response = await fetch(url.toString(), {
        method: "GET",
        headers: { ...headers, "Content-Type": "application/json" }
    });

    if (!response.ok) {
        throw new Error(`Getting chat histories failed: ${response.statusText}`);
    }

    const dataResponse: HistoryListApiResponse = await response.json();
    return dataResponse;
}

export async function getChatHistoryApi(id: string, idToken: string): Promise<HistoryApiResponse> {
    const headers = await getHeaders(idToken);
    const response = await fetch(`/chat_history/sessions/${id}`, {
        method: "GET",
        headers: { ...headers, "Content-Type": "application/json" }
    });

    if (!response.ok) {
        throw new Error(`Getting chat history failed: ${response.statusText}`);
    }

    const dataResponse: HistoryApiResponse = await response.json();
    return dataResponse;
}

export async function deleteChatHistoryApi(id: string, idToken: string): Promise<any> {
    const headers = await getHeaders(idToken);
    const response = await fetch(`/chat_history/sessions/${id}`, {
        method: "DELETE",
        headers: { ...headers, "Content-Type": "application/json" }
    });

    if (!response.ok) {
        throw new Error(`Deleting chat history failed: ${response.statusText}`);
    }
}
