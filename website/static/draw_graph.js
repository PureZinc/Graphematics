function drawGraph(canvasId, graphData, radius=10, edgeThickness=2) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');

    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Set canvas dimensions (proportional scaling)
    const canvasWidth = 500;
    const canvasHeight = 400;

    // Function to scale positions proportionally
    function scalePosition(pos, maxCanvasWidth, maxCanvasHeight) {
        const [x, y] = pos;
        const scaledX = x * canvas.width / maxCanvasWidth;
        const scaledY = y * canvas.height / maxCanvasHeight;
        return [scaledX, scaledY];
    }

    // Draw edges (lines between neighbors)
    Object.keys(graphData).forEach(vertexId => {
        const vertex = graphData[vertexId];
        const [x1, y1] = scalePosition(vertex.position, canvasWidth, canvasHeight);

        vertex.neighbors.forEach(neighborId => {
            const neighbor = graphData[neighborId];
            const [x2, y2] = scalePosition(neighbor.position, canvasWidth, canvasHeight);

            // Draw the line (edge)
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.strokeStyle = 'black';  // Edge color
            ctx.lineWidth = edgeThickness;  // Edge thickness
            ctx.stroke();
        });
    });

    // Draw vertices
    Object.keys(graphData).forEach(vertexId => {
        const vertex = graphData[vertexId];
        const [x, y] = scalePosition(vertex.position, canvasWidth, canvasHeight);

        // Draw the vertex (circle)
        ctx.beginPath();
        ctx.arc(x, y, radius, 0, 2 * Math.PI);  // Circle with radius 5
        ctx.fillStyle = vertex.labels[0];  // Vertex color
        ctx.fill();
    });
}