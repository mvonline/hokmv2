import React, { useState, useEffect, useCallback } from 'react';
import { Stage, Container, Graphics, Text } from '@pixi/react';
import * as PIXI from 'pixi.js';
import { GameClient } from '../lib/api';

interface Card {
    rank: string;
    suit: string;
}

interface Player {
    id: number;
    hand: Card[];
    won_tricks: number;
}

// Card Component
const CardSprite: React.FC<{ card: Card; x: number; y: number; onClick?: () => void }> = ({ card, x, y, onClick }) => {
    const draw = useCallback((g: PIXI.Graphics) => {
        g.clear();
        g.beginFill(0xFFFFFF);
        g.lineStyle(2, 0x000000);
        g.drawRoundedRect(0, 0, 80, 120, 10);
        g.endFill();
    }, []);

    return (
        <Container x={x} y={y} interactive={!!onClick} pointerdown={onClick}>
            <Graphics draw={draw} />
            <Text
                text={`${card.rank[0]}${card.suit[0]}`}
                x={10}
                y={10}
                style={new PIXI.TextStyle({ fontSize: 20, fill: ['#000000'] })}
            />
        </Container>
    );
};

export const Game: React.FC = () => {
    const [client, setClient] = useState<GameClient | null>(null);
    const [players, setPlayers] = useState<Player[]>([]);
    const [myId, setMyId] = useState<number>(0);
    const [gameState, setGameState] = useState<string>('Waiting');

    useEffect(() => {
        const newClient = new GameClient((msg) => {
            console.log('Received:', msg);
            // TODO: Handle game state updates
        });
        newClient.connect();
        setClient(newClient);

        // Mock data
        setPlayers([
            { id: 0, hand: [{ rank: 'Ace', suit: 'Spades' }, { rank: 'King', suit: 'Hearts' }, { rank: 'Queen', suit: 'Clubs' }], won_tricks: 0 },
            { id: 1, hand: [], won_tricks: 0 },
            { id: 2, hand: [], won_tricks: 0 },
            { id: 3, hand: [], won_tricks: 0 },
        ]);

        // Suppress unused variable warnings for now by logging them
        console.log("My ID:", myId);
        console.log("Game State:", gameState);
        setMyId(0);
        setGameState('Playing');

    }, [myId, gameState]);

    const playCard = (card: Card) => {
        console.log('Playing card:', card);
        if (client) {
            client.send({ type: 'PlayCard', card });
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
            <h1 className="text-3xl font-bold mb-4">Hokm v2 (Pixi.js)</h1>
            <div className="mb-2">State: {gameState}</div>

            <Stage width={800} height={600} options={{ backgroundColor: 0x1099bb }}>
                {/* Table Center */}
                <Graphics draw={(g) => {
                    g.clear();
                    g.lineStyle(4, 0xFFFFFF, 0.3);
                    g.drawCircle(400, 300, 100);
                }} />

                {/* My Hand (Bottom) */}
                <Container x={400} y={500}>
                    {players[0]?.hand.map((card, idx) => (
                        <CardSprite
                            key={idx}
                            card={card}
                            x={(idx - players[0].hand.length / 2) * 90}
                            y={0}
                            onClick={() => playCard(card)}
                        />
                    ))}
                </Container>

                {/* Opponent 1 (Left) */}
                <Container x={50} y={300}>
                    <Graphics draw={(g) => {
                        g.beginFill(0xFF0000);
                        g.drawCircle(0, 0, 30);
                        g.endFill();
                    }} />
                    <Text text="Opp 1" x={-20} y={40} style={new PIXI.TextStyle({ fill: 'white', fontSize: 14 })} />
                </Container>

                {/* Partner (Top) */}
                <Container x={400} y={50}>
                    <Graphics draw={(g) => {
                        g.beginFill(0x00FF00);
                        g.drawCircle(0, 0, 30);
                        g.endFill();
                    }} />
                    <Text text="Partner" x={-25} y={40} style={new PIXI.TextStyle({ fill: 'white', fontSize: 14 })} />
                </Container>

                {/* Opponent 2 (Right) */}
                <Container x={750} y={300}>
                    <Graphics draw={(g) => {
                        g.beginFill(0xFF0000);
                        g.drawCircle(0, 0, 30);
                        g.endFill();
                    }} />
                    <Text text="Opp 2" x={-20} y={40} style={new PIXI.TextStyle({ fill: 'white', fontSize: 14 })} />
                </Container>

            </Stage>
        </div>
    );
};
