import React from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

interface Link {
  href: string;
  title: string;
}

interface Section {
  heading: string;
  links: Link[];
}

interface SideNavProps {
  items: Section[]; // `items` is an array of `Section` objects
}


export function SideNav({ items }: SideNavProps) {
  const router = useRouter();

  return (
    <nav className="sidenav">
      {items.map((item, itemIndex) => (
        <div key={`item-${itemIndex}`}>
          {item.heading && <span>{item.heading}</span>}
          <ul className="flex column">
            {item.links.map((link, linkIndex) => {
              const active = router.pathname === link.href;
              return (
                <li
                  key={`link-${itemIndex}-${linkIndex}`}
                  className={active ? 'active' : ''}
                >
                  <Link href={link.href}>{link.title}</Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
      <style jsx>
        {`
          nav {
            position: sticky;
            top: var(--top-nav-height);
            height: calc(100vh - var(--top-nav-height));
            flex: 0 0 auto;
            overflow-y: auto;
            padding: 2.5rem 2rem 2rem;
            border-right: 1px solid var(--border-color);
          }
          span {
            font-size: larger;
            font-weight: 500;
            padding: 0.5rem 0 0.5rem;
          }
          ul {
            padding: 0;
          }
          li {
            list-style: none;
            margin: 0;
          }
          li :global(a) {
            text-decoration: none;
          }
          li :global(a:hover),
          li.active :global(a) {
            text-decoration: underline;
          }
        `}
      </style>
    </nav>
  );
}
