import { FunctionReference } from '../../components';

export const func = {
    render: FunctionReference,
    children: [],
    attributes: {
        href: {
            type: String,
            required: true,
        },
    },
};




interface Arg {
    name: string;
    type: string | null;
    desc: string;
}

interface Example {
    desc: string | null;
    code: string;
}


export interface FunctionDefinition {
    name: string;
    signature: string;
    summary: string;
    desc: string;
    args: Arg[];
    returns: string | null;
    examples: Example[];
}


const functionDefinition: FunctionDefinition = {
    name: 'Callout',
    signature: 'Callout',
    summary: 'A callout component for highlighting important information.',
    desc: 'The `Callout` component is used to highlight important information. It can be used to draw attention to a specific point, provide additional context, or offer a warning.',
    args: [
        {
            name: 'title',
            type: 'string',
            desc: 'The title of the callout.',
        },
    ],
    returns: null,
    examples: [
        {
            desc: 'A basic callout with a title and some content.',
            code: '```spam```',
        },
    ]
};
