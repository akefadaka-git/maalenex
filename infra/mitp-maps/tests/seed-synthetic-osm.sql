CREATE TABLE public.planet_osm_line (
    osm_id BIGINT PRIMARY KEY,
    highway TEXT NOT NULL,
    name TEXT,
    way geometry(Geometry, 3857) NOT NULL
);
CREATE INDEX planet_osm_line_way_gix ON public.planet_osm_line USING GIST (way);
INSERT INTO public.planet_osm_line (osm_id, highway, name, way)
VALUES (
    1, 'primary', 'Synthetic demonstration road',
    ST_Transform(ST_GeomFromText('LINESTRING(38 9, 38.08 9.06, 38.16 9.12)', 4326), 3857)
);

CREATE TABLE public.planet_osm_polygon (
    osm_id BIGINT PRIMARY KEY,
    landuse TEXT,
    natural TEXT,
    way geometry(Geometry, 3857) NOT NULL
);
CREATE INDEX planet_osm_polygon_way_gix ON public.planet_osm_polygon USING GIST (way);
INSERT INTO public.planet_osm_polygon (osm_id, landuse, natural, way)
VALUES (
    2, 'residential', NULL,
    ST_Transform(
        ST_GeomFromText(
            'POLYGON((37.98 8.98, 38.04 8.98, 38.04 9.04, 37.98 9.04, 37.98 8.98))',
            4326
        ),
        3857
    )
);
