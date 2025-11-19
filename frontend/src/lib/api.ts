export class GameClient {
    private ws: WebSocket | null = null;
    private onMessageCallback: (msg: any) => void;

    constructor(onMessage: (msg: any) => void) {
        this.onMessageCallback = onMessage;
    }

    connect() {
        this.ws = new WebSocket('ws://localhost:8080/ws/');

        this.ws.onopen = () => {
            console.log('Connected to server');
        };

        this.ws.onmessage = (event) => {
            try {
                // Handle text messages
                const data = JSON.parse(event.data);
                this.onMessageCallback(data);
            } catch (e) {
                console.log('Received non-JSON message:', event.data);
            }
        };

        this.ws.onclose = () => {
            console.log('Disconnected from server');
        };
    }

    send(data: any) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error('WebSocket is not connected');
        }
    }
}
