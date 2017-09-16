import * as d3 from "d3";

interface Graph {
    nodes: GraphNode[],
    links: GraphLink[],
}

interface GraphNode extends d3.SimulationNodeDatum {
    id: string,
    partition: number,
    p_tvEps: number,
    p_movie: number
    name: string,
    x: number,
    y: number,
    degree: number,
    degree_weight: number,
    degree_tvEps: number
    degree_movie: number,
    primaryProfession: string,
    birthYear: string,
    bio: string,
}

interface GraphLink extends d3.SimulationLinkDatum<d3.SimulationNodeDatum> {
    source: GraphNode,
    target: GraphNode,
    weight: number,
    w_tvEps: number,
    w_movie: number,
    // tconsts: string[],
}

export class Draw {
    json_path: string;
    svgId: string;
    weightFunc: (d: GraphLink) => number;
    degreeFunc: (d: GraphNode) => number;
    partitionFunc: (d: GraphNode) => string;

    color = d3.scaleOrdinal(d3.schemeCategory20);
    rScale = d3.scaleLinear()
        .domain([0, 100]) // min and max value in our data array
        .range([5, 40])
        .clamp(true);
    dScale = d3.scaleLinear()
        .domain([0, 100]) // min and max value in our data array
        .range([250, 40])
        .clamp(true);
    sScale = d3.scaleLinear()
        .domain([0, 100]) // min and max value in our data array
        .range([0.3, 1])
        .clamp(true);

    constructor(svgId: string, type: string, json_path: string) {
        this.svgId = svgId;
        this.json_path = json_path;

        if (type == 'all') {
            this.weightFunc = (d) => d.weight
            this.degreeFunc = (d) => this.rScale(d.degree_weight)
            this.partitionFunc = (d) => this.color(d.partition.toString())
        } else if (type == 'movie') {
            this.weightFunc = (d) => d.w_movie
            this.degreeFunc = (d) => this.rScale(d.degree_movie)
            this.partitionFunc = (d) => this.color(d.p_movie.toString())
        } else if (type == 'tvEps') {
            this.weightFunc = (d) => d.w_tvEps
            this.degreeFunc = (d) => this.rScale(d.degree_tvEps)
            this.partitionFunc = (d) => this.color(d.p_tvEps.toString())
        } else {
            console.log('wrong type')
        }
    }


    public render() {
        let svg = d3.select<SVGSVGElement, any>("svg" + '#' + this.svgId),
            width: number = +svg.attr("width"),
            height: number = +svg.attr("height");

        // name collision when using class, change simulation -> simulation1
        let simulation1 = d3.forceSimulation<GraphNode, GraphLink>()
            .force("link", d3.forceLink<GraphNode, GraphLink>()
                .id((d) => d.id)
                .distance((link) => this.dScale(this.weightFunc(link)))
                .strength((link) => this.sScale(this.weightFunc(link))))
            .force("charge", d3.forceManyBody())
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide<GraphNode>(this.degreeFunc)
                .strength(0.3))

        let that = this
        // let pathname = window.location.pathname;
        // window.alert('path: ' + pathname);
        d3.json<Graph>(this.json_path, function (error, graph) {
        // d3.json<Graph>(pathname + "../output/graph_200.json", function (error, graph) {
            if (error) throw error;

            let link = svg.append("g")
                .attr("class", "links")
                .selectAll<SVGPathElement, GraphLink>("path")
                .data(graph.links)
                .enter().append<SVGPathElement>("path")
                .attr("stroke-width", that.weightFunc);

            let node = svg.append("g")
                .attr("class", "nodes")
                .selectAll<SVGCircleElement, GraphNode>("circle")
                .data(graph.nodes)
                .enter().append<SVGCircleElement>("circle")
                .attr("r", that.degreeFunc)
                .attr("fill", that.partitionFunc)
                .call(d3.drag<SVGCircleElement, GraphNode>()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended))

            let text = svg.append("g")
                .attr("class", "labels")
                .selectAll<SVGTextElement, GraphNode>("text")
                .data(graph.nodes)
                .enter().append<SVGTextContentElement>("text")
                .attr('text-anchor', 'middle')
                .attr('fill', 'black')
                .attr('display', 'none')
                .text((d) => d.name)

            node
                .on('mouseover', (d) => {
                    text.filter((td) => td.name == d.name)
                        .transition()
                        .ease(d3.easeElastic)
                        .delay(100)
                        .duration(200)
                        .attr('display', 'on')
                    link.filter((ld) => ld.target == d || ld.source == d)
                        .transition()
                        .delay(100)
                        // use style to overwrite CSS
                        .style('stroke', '#ff0202')
                        .style('stroke-opacity', '1')
                        // cannot bring links to front
                        .each(function() {
                            this.parentElement!
                            .appendChild(this)
                          })
                })
                .on('mouseout', (d) => {
                    text.filter((td) => td.name == d.name)
                        .transition()
                        .delay(500)
                        .duration(500)
                        .attr('display', 'none')
                    link.filter((ld) => ld.target == d || ld.source == d)
                        .transition()
                        .delay(500)
                        .style('stroke', '#bbb')
                        .style('stroke-opacity', '0.6')
                })

            simulation1
                .nodes(graph.nodes)
                .on("tick", ticked);

            // Object is possibly 'null' or 'undefined'
            // https://stackoverflow.com/a/40350534/8453575
            simulation1.force<d3.ForceLink<GraphNode, GraphLink>>("link")!
                .links(graph.links);
            // another solution:
            // https://github.com/Microsoft/TypeScript/issues/10642
            // const forceLink = simulation.force<d3.ForceLink<GraphNode, GraphLink>>("link")
            // if (forceLink) {
            //     forceLink.links(graph.links);
            // }

            function ticked() {
                // link.attr("d", d3.line<[number, number]>()
                // .x(function(d) { return x(d.source.x); })
                // .y(function(d) { return y(d.source.y); }
                // .curve(d3.curveNatural));
                link.attr("d", function (d) {
                    let dx = d.target.x - d.source.x,
                        dy = d.target.y - d.source.y,
                        dr = Math.sqrt(dx * dx + dy * dy);
                    return "M" + d.source.x + "," + d.source.y
                        // + "S" + dr + "," + dr
                        + "A" + dr + "," + dr + " 0 0,1 "
                        + d.target.x + "," + d.target.y;
                });
                // .curve(d3.curveCardinal));
                // .attr("x1", (d) => d.source.x)
                // .attr("y1", (d) => d.source.y)
                // .attr("x2", (d) => d.target.x)
                // .attr("y2", (d) => d.target.y);

                // node
                //     .attr("x", (d) => d.x)
                //     .attr("y", (d) => d.y);
                node.attr("transform", (d) => "translate(" + d.x + "," + d.y + ")")
                text.attr("transform", (d) => "translate(" + d.x + "," + d.y + ")")
            }
        });

        function dragstarted(d: GraphNode) {
            if (!d3.event.active) simulation1.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(d: GraphNode) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragended(d: GraphNode) {
            if (!d3.event.active) simulation1.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
    }
}

export function draw(svgId: string, type: string, json_path: string): void {
    let d = new Draw(svgId, type, json_path);
    d.render();
}


// draw('movie');