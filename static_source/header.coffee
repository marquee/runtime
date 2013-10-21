console.log 'header.coffee'
is_mobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent)

# TODO: widget-ify this kind of overflow nav

$window = $(window)
$nav    = $('#site-header .category_nav')

FIXED_ORDER = ['la', 'electronic', 'unearthed']
first_categories = {}
other_categories = []

_.each params.categories, (cat) ->
    if cat.slug in FIXED_ORDER
        first_categories[cat.slug] = (cat)
    else
        other_categories.push(cat)
first_categories = _.map FIXED_ORDER, (slug) -> first_categories[slug]

console.log "asdf", first_categories

$popover = $("""
        <div class="popover">
            <span class="popover_closer"></span>
            <span class="popover_trigger">More</span>
            <div class="popover_content"></div>
        </div>
    """)



$popover_content = $popover.find('.popover_content')
$popover_trigger = $popover.find('.popover_trigger')

if is_mobile
    $popover.attr('data-touch', true)
    popover_is_open = false
    last_touch = new Date()
    togglePopover = ->
        now = new Date()
        # Avoid doing things too quickly, or allowing repeat actions since this
        # is triggered by different events that can happen at the same time.
        unless now - last_touch < 500
            _.defer ->
                if popover_is_open
                    $popover.removeAttr('data-active')
                    popover_is_open = false
                else
                    $popover.attr('data-active', true)
                    popover_is_open = true
            last_touch = now
    $popover_trigger.on('touchend', togglePopover)
    $popover.find('.popover_closer').on('click', togglePopover)


makeCategoryLink = (cat) ->
    return "<a href='/category/#{ cat.slug }/'>#{ cat.title }</a>"



renderPopover = (lists...) ->
    $popover_content.empty()
    for list in lists
        _.each list, (cat) ->
            $popover_content.append(makeCategoryLink(cat))



renderNav = ->
    $nav.empty()
    if $window.width() <= 700
        console.log 'all in'
        renderPopover(first_categories, other_categories)
        $popover_trigger.text('Categories')
    else
        _.each first_categories, (cat) ->
            $nav.append(makeCategoryLink(cat))
        renderPopover(other_categories)
        $popover_trigger.text('More')
    $nav.append($popover)



$window.on 'resize', _.debounce(renderNav, 50)
renderNav()


