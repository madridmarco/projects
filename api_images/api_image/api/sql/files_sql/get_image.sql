    with
        base_inicial as (
            select
                  id
                , date_format(date, '%Y-%m-%d %H:%i:%s') as date
                , path
            from pictures
            where id = _id_
        )

        ,base_final as (
            select
                  t1.*
                , t2.tag
                , t2.confidence
            from base_inicial t1
            inner join tags t2
                on t1.id = t2.picture_id
        )
    select * from base_final