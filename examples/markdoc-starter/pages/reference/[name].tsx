// pages/reference/[pageName].tsx

import { useRouter } from 'next/router';
import { FunctionReference } from '../../components';
const ReferencePage: React.FC = () => {
    const router = useRouter();
    const { name } = router.query; // Get the pageName from the URL

    if (!name) {
        return <p>Loading...</p>; // Or some other loading indicator
    }

    return <>
        <FunctionReference href={name} >
            <p></p>
        </FunctionReference >
    </>
};

export default ReferencePage;
