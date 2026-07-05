import { Card } from './card.model'

export class BoosterSet {
	constructor(
		public name: string,
		public url: string,
		public cards: Card[] = [],
		public code?: string,
		public generation?: string,
		public number?: string,
	) {}

	toJSON() {
		return {
			name: this.name,
			url: this.url,
			code: this.code,
			generation: this.generation,
			number: this.number,
			cards: this.cards.map(c => c.toJSON())
		}
	}

	static fromJSON(json: any): BoosterSet {
		return new BoosterSet(
			json.name || 'Unknown',
			json.url || '',
			Array.isArray(json?.cards)
				? json.cards.map((cj: any) => Card.fromJSON(cj))
				: [],
			json.code,
			json.generation,
			json.number,
		)
	}
}