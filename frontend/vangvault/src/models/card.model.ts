export type CardType = 'Unit' | 'Order' | 'Other'
export type UnitSubtype = 'Normal' | 'Trigger'
export type OrderSubtype = 'Normal' | 'Blitz'

export abstract class Card {
	id?: string
	name: string
	cardType: CardType

	constructor(name: string, cardType: CardType, id?: string) {
		this.name = name
		this.cardType = cardType
		this.id = id
	}

	abstract toJSON(): any
	static fromJSON(json: any): Card {
		// simple factory delegando según cardType
		const t = (json?.cardType || json?.type || 'Other') as CardType
		if (t === 'Unit') return Unit.fromJSON(json)
		if (t === 'Order') return Order.fromJSON(json)
		return OtherCard.fromJSON(json)
	}
}

export class Unit extends Card {
	subtype: UnitSubtype
	// campos mínimos; irás añadiendo más (power, nation, etc.)
	constructor(name: string, subtype: UnitSubtype = 'Normal', id?: string) {
		super(name, 'Unit', id)
		this.subtype = subtype
	}

	toJSON() {
		return { id: this.id, name: this.name, cardType: this.cardType, subtype: this.subtype }
	}

	static fromJSON(json: any) {
		const u = new Unit(json.name || 'Unknown', (json.subtype as UnitSubtype) || 'Normal', json.id)
		return u
	}
}

export class Order extends Card {
	subtype: OrderSubtype
	constructor(name: string, subtype: OrderSubtype = 'Normal', id?: string) {
		super(name, 'Order', id)
		this.subtype = subtype
	}

	toJSON() {
		return { id: this.id, name: this.name, cardType: this.cardType, subtype: this.subtype }
	}

	static fromJSON(json: any) {
		return new Order(json.name || 'Unknown', (json.subtype as OrderSubtype) || 'Normal', json.id)
	}
}

export class OtherCard extends Card {
	data: any
	constructor(name: string, data: any = {}, id?: string) {
		super(name, 'Other', id)
		this.data = data
	}
	toJSON() {
		return { id: this.id, name: this.name, cardType: this.cardType, data: this.data }
	}
	static fromJSON(json: any) {
		return new OtherCard(json.name || 'Unknown', json.data || {}, json.id)
	}
}
