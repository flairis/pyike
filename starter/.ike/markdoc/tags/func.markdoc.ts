import { FuncReference } from '../../components';

export const func = {
    render: FuncReference,
    children: [],
    attributes: {
        name: {
            type: String,
            required: true,
        },
    },
    selfClosing: true,
};
