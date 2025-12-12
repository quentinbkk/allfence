import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Card,
  CardContent,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Storage as StorageIcon,
  AccountTree as SchemaIcon,
  Link as RelationIcon,
  Description as MetadataIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`data-structure-tabpanel-${index}`}
      aria-labelledby={`data-structure-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const DataStructurePage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Database schema definition
  const databaseSchema = [
    {
      table: 'clubs',
      description: 'Represents fencing clubs/associations where fencers are registered',
      primaryKey: 'club_id',
      fields: [
        { name: 'club_id', type: 'String', nullable: false, description: 'Unique identifier (Primary Key)' },
        { name: 'club_name', type: 'String', nullable: false, description: 'Name of the club' },
        { name: 'start_year', type: 'Integer', nullable: true, description: 'Year club was founded' },
        { name: 'status', type: 'String', nullable: true, description: 'Status: Active, Inactive, Pending' },
        { name: 'weapon_club', type: 'String', nullable: true, description: 'Primary weapon specialization' },
      ],
      relationships: [
        { type: 'one-to-many', target: 'fencers', description: 'One club has many fencers' },
      ],
    },
    {
      table: 'fencers',
      description: 'Core entity storing individual fencer information',
      primaryKey: 'fencer_id',
      fields: [
        { name: 'fencer_id', type: 'Integer', nullable: false, description: 'Unique identifier (Primary Key)' },
        { name: 'first_name', type: 'String', nullable: false, description: 'First name' },
        { name: 'last_name', type: 'String', nullable: false, description: 'Last name' },
        { name: 'dob', type: 'Date', nullable: false, description: 'Date of birth' },
        { name: 'gender', type: 'String(1)', nullable: false, description: 'Gender: M or F' },
        { name: 'weapon', type: 'String', nullable: false, description: 'Weapon: Sabre, Foil, or Epee' },
        { name: 'club_id', type: 'String', nullable: true, description: 'Foreign Key to clubs table' },
      ],
      relationships: [
        { type: 'many-to-one', target: 'clubs', description: 'Many fencers belong to one club' },
        { type: 'one-to-many', target: 'rankings', description: 'One fencer has multiple rankings (per bracket)' },
        { type: 'one-to-many', target: 'tournament_results', description: 'One fencer has many tournament results' },
      ],
    },
    {
      table: 'tournaments',
      description: 'Represents fencing competitions and events',
      primaryKey: 'tournament_id',
      fields: [
        { name: 'tournament_id', type: 'String', nullable: false, description: 'Unique identifier (Primary Key)' },
        { name: 'tournament_name', type: 'String', nullable: false, description: 'Name of the tournament' },
        { name: 'date', type: 'Date', nullable: false, description: 'Tournament date' },
        { name: 'location', type: 'String', nullable: true, description: 'Tournament location' },
        { name: 'weapon', type: 'String', nullable: false, description: 'Weapon discipline' },
        { name: 'bracket', type: 'String', nullable: false, description: 'Age bracket' },
        { name: 'competition_type', type: 'String', nullable: false, description: 'Type: National, Regional, Local' },
        { name: 'status', type: 'String', nullable: false, description: 'Status: Completed, Scheduled, Cancelled' },
        { name: 'season_id', type: 'Integer', nullable: true, description: 'Foreign Key to seasons table' },
      ],
      relationships: [
        { type: 'many-to-one', target: 'seasons', description: 'Many tournaments belong to one season' },
        { type: 'one-to-many', target: 'tournament_results', description: 'One tournament has many results' },
      ],
    },
    {
      table: 'tournament_results',
      description: 'Stores individual fencer results from tournaments',
      primaryKey: 'result_id',
      fields: [
        { name: 'result_id', type: 'Integer', nullable: false, description: 'Unique identifier (Primary Key)' },
        { name: 'tournament_id', type: 'String', nullable: false, description: 'Foreign Key to tournaments' },
        { name: 'fencer_id', type: 'Integer', nullable: false, description: 'Foreign Key to fencers' },
        { name: 'rank', type: 'Integer', nullable: false, description: 'Final placement in tournament' },
        { name: 'points_awarded', type: 'Float', nullable: false, description: 'Ranking points earned' },
      ],
      relationships: [
        { type: 'many-to-one', target: 'tournaments', description: 'Many results belong to one tournament' },
        { type: 'many-to-one', target: 'fencers', description: 'Many results belong to one fencer' },
      ],
    },
    {
      table: 'rankings',
      description: 'Current ranking standings for fencers in their brackets',
      primaryKey: 'ranking_id',
      fields: [
        { name: 'ranking_id', type: 'Integer', nullable: false, description: 'Unique identifier (Primary Key)' },
        { name: 'fencer_id', type: 'Integer', nullable: false, description: 'Foreign Key to fencers' },
        { name: 'bracket_name', type: 'String', nullable: false, description: 'Age bracket name' },
        { name: 'points', type: 'Float', nullable: false, description: 'Total ranking points' },
        { name: 'rank', type: 'Integer', nullable: true, description: 'Current rank in bracket' },
        { name: 'tournaments_attended', type: 'Integer', nullable: false, description: 'Number of tournaments' },
      ],
      relationships: [
        { type: 'many-to-one', target: 'fencers', description: 'Many rankings belong to one fencer' },
      ],
    },
    {
      table: 'seasons',
      description: 'Represents competitive seasons for organizing tournaments',
      primaryKey: 'season_id',
      fields: [
        { name: 'season_id', type: 'Integer', nullable: false, description: 'Unique identifier (Primary Key)' },
        { name: 'name', type: 'String', nullable: false, description: 'Season name (e.g., 2024-2025)' },
        { name: 'start_date', type: 'Date', nullable: false, description: 'Season start date' },
        { name: 'end_date', type: 'Date', nullable: false, description: 'Season end date' },
        { name: 'status', type: 'String', nullable: false, description: 'Status: Active, Completed, Upcoming' },
        { name: 'description', type: 'String', nullable: true, description: 'Optional description' },
      ],
      relationships: [
        { type: 'one-to-many', target: 'tournaments', description: 'One season has many tournaments' },
      ],
    },
  ];

  // Data organization metadata
  const dataOrganization = {
    purpose: 'Fencing Management System for tracking tournaments, fencers, clubs, and rankings',
    scope: 'Information Organization and Retrieval - Final Project',
    entities: 6,
    relationships: 9,
    architecture: 'Relational Database with RESTful API',
  };

  // API endpoints structure
  const apiEndpoints = [
    {
      category: 'Fencers',
      endpoints: [
        { method: 'GET', path: '/api/fencers', description: 'Get all fencers with filters' },
        { method: 'GET', path: '/api/fencers/:id', description: 'Get specific fencer details' },
      ],
    },
    {
      category: 'Clubs',
      endpoints: [
        { method: 'GET', path: '/api/clubs', description: 'Get all clubs' },
        { method: 'GET', path: '/api/clubs/:id', description: 'Get club details with members' },
        { method: 'GET', path: '/api/clubs/:id/cumulative-points', description: 'Get club points over time' },
      ],
    },
    {
      category: 'Tournaments',
      endpoints: [
        { method: 'GET', path: '/api/tournaments', description: 'Get all tournaments with filters' },
        { method: 'GET', path: '/api/tournaments/:id', description: 'Get tournament details' },
        { method: 'GET', path: '/api/tournaments/:id/results', description: 'Get tournament results' },
      ],
    },
    {
      category: 'Rankings',
      endpoints: [
        { method: 'GET', path: '/api/rankings', description: 'Get fencer rankings by bracket/weapon' },
        { method: 'GET', path: '/api/rankings/clubs', description: 'Get club rankings by weapon' },
        { method: 'GET', path: '/api/rankings/clubs/cumulative-points', description: 'Get all clubs cumulative points' },
      ],
    },
    {
      category: 'Seasons',
      endpoints: [
        { method: 'GET', path: '/api/seasons', description: 'Get all seasons' },
        { method: 'POST', path: '/api/seasons', description: 'Create new season' },
      ],
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <StorageIcon fontSize="large" />
          Data Structure & Organization
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive overview of the AllFence system architecture, data models, and API structure
        </Typography>
      </Box>

      {/* Project Metadata Card */}
      <Card sx={{ mb: 3, bgcolor: '#f5f5f5' }}>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <MetadataIcon />
            Project Metadata
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Purpose</Typography>
              <Typography variant="body1">{dataOrganization.purpose}</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" color="text.secondary">Scope</Typography>
              <Typography variant="body1">{dataOrganization.scope}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">Database Entities</Typography>
              <Typography variant="h5" color="primary">{dataOrganization.entities}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">Relationships</Typography>
              <Typography variant="h5" color="primary">{dataOrganization.relationships}</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body2" color="text.secondary">Architecture</Typography>
              <Typography variant="body1">{dataOrganization.architecture}</Typography>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs for different views */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<SchemaIcon />} label="Database Schema" />
          <Tab icon={<RelationIcon />} label="Relationships" />
          <Tab icon={<StorageIcon />} label="API Endpoints" />
        </Tabs>

        {/* Tab 1: Database Schema */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            Database Tables & Fields
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Detailed schema of all database tables, their fields, types, and constraints
          </Typography>

          {databaseSchema.map((table, index) => (
            <Accordion key={index} defaultExpanded={index === 0}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                  <Typography variant="h6" sx={{ fontFamily: 'monospace', color: 'primary.main' }}>
                    {table.table}
                  </Typography>
                  <Chip label={`PK: ${table.primaryKey}`} size="small" color="primary" />
                  <Typography variant="body2" color="text.secondary" sx={{ flex: 1 }}>
                    {table.description}
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>Field Name</strong></TableCell>
                        <TableCell><strong>Data Type</strong></TableCell>
                        <TableCell><strong>Nullable</strong></TableCell>
                        <TableCell><strong>Description</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {table.fields.map((field, idx) => (
                        <TableRow key={idx}>
                          <TableCell sx={{ fontFamily: 'monospace', fontWeight: field.name === table.primaryKey ? 'bold' : 'normal' }}>
                            {field.name}
                          </TableCell>
                          <TableCell>
                            <Chip label={field.type} size="small" variant="outlined" />
                          </TableCell>
                          <TableCell>
                            {field.nullable ? (
                              <Chip label="Yes" size="small" color="default" />
                            ) : (
                              <Chip label="No" size="small" color="error" />
                            )}
                          </TableCell>
                          <TableCell>{field.description}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          ))}
        </TabPanel>

        {/* Tab 2: Relationships */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            Entity Relationships
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Visual representation of how database tables relate to each other
          </Typography>

          <Grid container spacing={3}>
            {databaseSchema.map((table, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" sx={{ fontFamily: 'monospace', mb: 2, color: 'primary.main' }}>
                      {table.table}
                    </Typography>
                    <Divider sx={{ mb: 2 }} />
                    {table.relationships.length > 0 ? (
                      table.relationships.map((rel, idx) => (
                        <Box key={idx} sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Chip
                            label={rel.type}
                            size="small"
                            color={rel.type.includes('one-to-many') ? 'success' : 'info'}
                          />
                          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                            → {rel.target}
                          </Typography>
                        </Box>
                      ))
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No direct relationships
                      </Typography>
                    )}
                    <Divider sx={{ my: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                      {table.description}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </TabPanel>

        {/* Tab 3: API Endpoints */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            RESTful API Endpoints
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Complete list of API endpoints for data retrieval and manipulation
          </Typography>

          {apiEndpoints.map((category, index) => (
            <Accordion key={index} defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6" color="primary.main">
                  {category.category}
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell width="100px"><strong>Method</strong></TableCell>
                        <TableCell><strong>Endpoint</strong></TableCell>
                        <TableCell><strong>Description</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {category.endpoints.map((endpoint, idx) => (
                        <TableRow key={idx}>
                          <TableCell>
                            <Chip
                              label={endpoint.method}
                              size="small"
                              color={endpoint.method === 'GET' ? 'info' : 'success'}
                            />
                          </TableCell>
                          <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.9rem' }}>
                            {endpoint.path}
                          </TableCell>
                          <TableCell>{endpoint.description}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </AccordionDetails>
            </Accordion>
          ))}
        </TabPanel>
      </Paper>

      {/* Data Flow Overview */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            System Data Flow
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            The AllFence system follows a three-tier architecture:
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, bgcolor: '#e3f2fd', height: '100%' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  1. Data Layer (Backend)
                </Typography>
                <Typography variant="body2">
                  SQLite database with SQLAlchemy ORM managing 6 core entities and their relationships.
                  Includes data validation, constraints, and integrity checks.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, bgcolor: '#f3e5f5', height: '100%' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  2. API Layer (Flask)
                </Typography>
                <Typography variant="body2">
                  RESTful API with 20+ endpoints for CRUD operations, complex queries, aggregations,
                  and time-series data retrieval.
                </Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2, bgcolor: '#e8f5e9', height: '100%' }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  3. Presentation Layer (React)
                </Typography>
                <Typography variant="body2">
                  React frontend with RTK Query for state management, Material-UI for components,
                  and Recharts for data visualization.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Container>
  );
};

export default DataStructurePage;
