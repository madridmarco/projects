with
    filter_date as (
        select
              id
            , date
            , path
        from pictures
        where date replace_filter_date
    )
    
    ,filter_for_tag as (
        select
              t2.id
            , date_format(t2.date, '%Y-%m-%d %H:%i:%s') as date
            , t1.tag
            , t1.confidence
            , t2.path
        from tags t1
        inner join filter_date t2
            on t2.id = t1.picture_id
                tags_
    )
select * from filter_for_tag;