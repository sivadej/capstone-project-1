--movies
INSERT INTO public.movies (
netflix_id, title, image_url, synopsis, year, rating, video_type) VALUES (
'1'::integer, 'Iron Man'::character varying(50), 'https://www.fillmurray.com/360/500'::character varying, 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
'::text, '2000'::integer, 'PG'::character varying(5), 'movie'::character varying(8))
 returning id;

--users

--watchlists

--watchlists_movies